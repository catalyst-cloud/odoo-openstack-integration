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

from odoo import api, fields, models


class OpenStackProject(models.Model):
    """A Project, attached to partner"""

    _name = "openstack.project"
    _description = "OpenStack Project"
    _rec_name = "display_name"
    _inherit = ["mail.thread"]

    name = fields.Char(string="Project Name", required=True)
    os_id = fields.Char(
        string="Project ID",
        required=True,
        unique=True,
    )

    @api.depends("name", "os_id")
    def _get_name(self):
        """Computed field to show in the breadcrumbs"""
        for project in self:
            project.display_name = f"{project.name} ({project.os_id})"

    display_name = fields.Char(string="Display Name", compute="_get_name", store=True)

    parent = fields.Many2one(comodel_name="openstack.project", string="Parent Project")
    enabled = fields.Boolean(string="Enabled", default=True)

    billing_type = fields.Selection(
        selection=[
            ("customer", "customer"),
            ("internal", "internal"),
        ],
        default="customer",
        string="Billing Type",
        required=True,
    )

    group_invoices = fields.Boolean(string="Group Invoices")

    payment_method = fields.Selection(
        selection=[("credit_card", "credit_card"), ("invoice", "invoice")],
        default="invoice",
        string="Payment Method",
        required=True,
    )
    stripe_card_id = fields.Char("Stripe Card ID", required=False)
    po_number = fields.Char(string="PO Number")
    override_po_number = fields.Boolean(string="Override PO Number")

    owner = fields.Many2one(
        comodel_name="res.partner", string="Owner partner", required=True
    )
    project_contacts = fields.One2many(
        comodel_name="openstack.project_contact",
        inverse_name="project",
        string="Project Contacts",
    )

    project_credits = fields.One2many(
        comodel_name="openstack.credit",
        inverse_name="project",
        string="Credits",
    )
    project_grants = fields.One2many(
        comodel_name="openstack.grant",
        inverse_name="project",
        string="Grants",
    )
    term_discounts = fields.One2many(
        comodel_name="openstack.term_discount",
        inverse_name="project",
        string="Term Discounts",
    )

    support_subscription = fields.Many2one(
        comodel_name="openstack.support_subscription",
        string="Premium Support Subscription",
    )


class OpenStackProjectContacts(models.Model):
    """Bridge table for openstack project and a partner"""

    _name = "openstack.project_contact"
    _description = "OpenStack Project Contacts bridge table"

    project = fields.Many2one(comodel_name="openstack.project", string="Project")
    partner = fields.Many2one(
        comodel_name="res.partner", string="Partner", required=True
    )
    inherit = fields.Boolean(
        string="Inherit to sub-projects",
        default=False,
    )

    contact_type = fields.Selection(
        selection=[
            ("primary", "primary"),
            ("billing", "billing"),
            ("technical", "technical"),
            ("legal", "legal"),
            # TODO(adriant): REMOVE RESELLER LATER:
            ("reseller customer", "reseller customer"),
        ],
        string="Contact Type",
        required=True,
    )
