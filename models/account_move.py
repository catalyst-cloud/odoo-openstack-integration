# Copyright (C) 2021-2024 Catalyst Cloud Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import datetime

from odoo import fields, models


def credit_and_debit(input, old_credit=0, old_debit=0):
    if input < 0:
        return old_credit + input, old_debit
    return old_credit, old_debit + input


class InvoiceRegionCategory:
    def __init__(self):
        self.lines = []
        self.count = 0
        self.credit = 0
        self.debit = 0
        self.name = ""

    def total(self):
        return self.credit + self.debit

    def add_region(self, line):
        self.name = line.product_id.categ_id.parent_id["name"]
        self.credit, self.debit = credit_and_debit(
            line.price_subtotal, self.credit, self.debit
        )
        self.count += 1

        self.lines.append(line)


class InvoiceProductCategory:
    def __init__(self):
        self.regions = {}
        self.count = 0
        self.credit = 0
        self.debit = 0
        self.name = ""
        self.uncategorised = []

    def total(self):
        return self.credit + self.debit

    def add_product(self, line):
        product = line.product_id
        self.credit, self.debit = credit_and_debit(
            line.price_subtotal, self.credit, self.debit
        )
        self.count += 1

        if product and product.categ_id and product.categ_id.parent_id:
            self.name = product.categ_id["name"]
            region_name = product.categ_id.parent_id["name"]
            try:
                region_group = self.regions[region_name]
                region_group.add_region(line)
            except KeyError:
                self.regions[region_name] = InvoiceRegionCategory()
                self.regions[region_name].add_region(line)
        else:
            self.uncategorised.append(line)


class CategorisedInvoice:
    def __init__(self):
        self.products = {}
        self.count = 0
        self.credit = 0
        self.debit = 0
        self.uncategorised = []

    def total(self):
        return self.credit + self.debit

    def add_line(self, line):
        product = line.product_id
        self.credit, self.debit = credit_and_debit(
            line.price_subtotal, self.credit, self.debit
        )
        self.count += 1

        if product and product.categ_id:
            product_name = product.categ_id["name"]
            try:
                product_group = self.products[product_name]
                product_group.add_product(line)
            except KeyError:
                self.products[product_name] = InvoiceProductCategory()
                self.products[product_name].add_product(line)
        else:
            self.uncategorised.append(line)


class OutstandingInvoices:
    def __init__(self):
        self.old_invoices = []
        self.current_invoices = []

    def _reset(self):
        # use instead of reinit OutStandingInvoices - report_invoice.xml template is
        # already tracking this object. But if we re-run invoicing in quick
        # succession without resetting these, the contents will be doubled up.
        # It's probably cursed.
        self.old_invoices = []
        self.current_invoices = []

    def ordered_old_invoices(self):
        return sorted(self.old_invoices, key=lambda x: x["invoice_date_due"])

    def ordered_current_invoices(self):
        return sorted(self.current_invoices, key=lambda x: x["invoice_date_due"])

    def total_owing(self):
        return self.old_owing() + self.current_owing()

    def old_owing(self):
        sum = 0

        for inv in self.old_invoices:
            sum = sum + inv["amount_residual_signed"]
        return sum

    def current_owing(self):
        sum = 0
        for inv in self.current_invoices:
            sum = sum + inv["amount_residual_signed"]
        return sum

    def add(self, invoices):
        for invoice in invoices:
            # temp dict to prevent attempting deeper calls on the object when
            # connection has closed just pulls the relevant values and stores them
            # for recall later.
            temp_invoice = {
                "invoice_date_due": invoice.invoice_date_due,
                "amount_residual_signed": invoice.amount_residual_signed,
                "name": invoice.name,
            }

            if datetime.date.today() > invoice.invoice_date_due:
                self.old_invoices.append(temp_invoice)
            else:
                self.current_invoices.append(temp_invoice)


class AccountMove(models.Model):
    _inherit = "account.move"
    outstanding_invoices = OutstandingInvoices()

    os_project = fields.Many2one(
        comodel_name="openstack.project",
        string="OpenStack Project",
    )

    os_is_cloud_framework_agreement_invoice = fields.Boolean(
        string="CFA invoice",
        default=False,
        required=False,
    )

    def is_openstack_invoice(self):
        """Return whether this is an OpenStack invoice."""

        return bool(self.os_project)

    def categorised_openstack_invoice_lines(self):
        """Group invoice lines by project and categorise"""

        categorised_invoice = CategorisedInvoice()

        for line in self.invoice_line_ids:
            categorised_invoice.add_line(line)
        return categorised_invoice

    def get_outstanding_invoices(self, project_id, partner_id):
        if not project_id:
            return self.env["account.move"].search(
                [
                    ("amount_residual_signed", ">", 0),
                    ("partner_id.id", "=", partner_id["id"]),
                ]
            )

        return self.env["account.move"].search(
            [
                ("amount_residual_signed", ">", 0),
                ("os_project.id", "=", project_id["id"]),
            ]
        )

    def send_openstack_invoice_email(self, email_ctx=None):
        # reset before, to ensure data is current
        self.outstanding_invoices._reset()
        try:
            if email_ctx is None:
                email_ctx = {}
            template_id = self.env.ref(
                "openstack_integration.email_template_openstack_invoice"
            ).with_context(**email_ctx)
            for invoice in self:
                if invoice["is_move_sent"]:
                    continue
                outstanding = self.get_outstanding_invoices(
                    invoice.os_project, invoice.partner_id
                )
                for inv in outstanding:
                    self.outstanding_invoices.add(inv)
                csv_data = self.env.ref(
                    "openstack_integration.openstack_invoice_csv"
                )._render_csv([invoice.id], False)[0]
                csv_data_encoded = base64.encodebytes(csv_data.encode("utf-8"))
                invoice_name = (invoice.state == "posted") and (
                    (invoice.name or "INV").replace("/", "_")
                )
                filename = "Detail_{}.csv".format(invoice_name)
                attachment = {
                    "name": filename,
                    "datas": csv_data_encoded,
                    "store_fname": filename,
                    "res_model": "account.move",
                    "type": "binary",  # "binary" just means file, as opposed to "url"
                    "res_id": invoice.id,
                    "mimetype": "text/csv",
                }
                attachment_id = self.env["ir.attachment"].create(attachment)
                # Set additional attachment, send, remove attachments again
                template_id.attachment_ids = [(6, 0, [attachment_id.id])]
                template_id.send_mail(invoice.id)
                template_id.attachment_ids = False

                invoice.write({"is_move_sent": True})
        finally:
            # Reset after - avoids manually generated Statement Of Accounts issues
            self.outstanding_invoices._reset()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    os_project = fields.Many2one(
        comodel_name="openstack.project",
        string="OpenStack Project",
    )

    os_region = fields.Text(
        string="OS Region",
        required=False,
    )

    os_resource_type = fields.Text(
        string="OS Resource Type",
        required=False,
    )

    os_resource_name = fields.Text(
        string="OS Resource Name",
        required=False,
    )

    os_resource_id = fields.Text(
        string="OS Resource ID",
        required=False,
    )
