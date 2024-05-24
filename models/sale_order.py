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

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    os_project = fields.Many2one(
        comodel_name="openstack.project",
        string="OpenStack Project",
    )

    # NOTE(adriant): because odoo is stupid...
    # NOTE(TODO): move this into standalone addon
    os_invoice_date = fields.Date(
        string="Invoice Date",
        required=False,
    )

    os_invoice_due_date = fields.Date(
        string="Invoice Due Date",
        required=False,
    )

    os_is_cloud_framework_agreement_sale_order = fields.Boolean(
        string="CFA Sale Order",
        default=False,
        required=False,
    )

    def create_invoices(self):
        sale_order_ids = [s.id for s in self]
        payment = self.env["sale.advance.payment.inv"].create(
            {"advance_payment_method": "delivered"}
        )
        payment.with_context(active_ids=sale_order_ids).create_invoices()

    def _prepare_invoice(self):
        self.ensure_one()
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals["os_project"] = self.os_project.id
        if self.os_invoice_date:
            invoice_vals["invoice_date"] = self.os_invoice_date
        if self.os_invoice_due_date:
            invoice_vals["invoice_date_due"] = self.os_invoice_due_date
        invoice_vals["os_is_cloud_framework_agreement_invoice"] = False
        if self.os_is_cloud_framework_agreement_sale_order:
            invoice_vals["os_is_cloud_framework_agreement_invoice"] = (
                self.os_is_cloud_framework_agreement_sale_order
            )
        return invoice_vals


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

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

    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        invoice_line_vals = super(SaleOrderLine, self)._prepare_invoice_line()
        invoice_line_vals["os_project"] = self.os_project.id

        invoice_line_vals["os_region"] = "NZ"
        invoice_line_vals["os_resource_type"] = ""
        invoice_line_vals["os_resource_name"] = ""
        invoice_line_vals["os_resource_id"] = ""

        if self.os_region:
            invoice_line_vals["os_region"] = self.os_region
        if self.os_resource_type:
            invoice_line_vals["os_resource_type"] = self.os_resource_type
        if self.os_resource_name:
            invoice_line_vals["os_resource_name"] = self.os_resource_name
        if self.os_resource_id:
            invoice_line_vals["os_resource_id"] = self.os_resource_id

        return invoice_line_vals
