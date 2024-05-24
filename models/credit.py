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

from datetime import date

from odoo import _, api, fields, models, exceptions


class OpenStackCredit(models.Model):
    """OpenStack credit which is attached to a project"""

    _name = "openstack.credit"
    _description = "OpenStack Credit"

    voucher_code = fields.Many2one(
        comodel_name="openstack.voucher_code", string="Voucher Code"
    )

    project = fields.Many2one(
        comodel_name="openstack.project",
        string="Project",
        required=True,
    )

    @api.depends("project", "voucher_code")
    def _get_name(self):
        """Computed field to show in the breadcrumbs"""
        for credit in self:
            name = credit.project.name
            if credit.voucher_code:
                name = f"{credit.project.name} - {credit.voucher_code.name}"
            credit.name = name

    name = fields.Char(string="Name", compute="_get_name")

    credit_type = fields.Many2one(
        comodel_name="openstack.credit.type",
        string="Credit Type",
        required=True,
    )

    start_date = fields.Date(string="Start Date", required=True, default=date.today())
    expiry_date = fields.Date(string="Expiry Date")

    initial_balance = fields.Float(string="Initial Balance", required=True)

    current_balance = fields.Float(string="Current Balance", compute="_compute_balance")

    transactions = fields.One2many(
        comodel_name="openstack.credit.transaction",
        inverse_name="credit",
        string="Credit Transactions",
    )

    @api.depends("initial_balance")
    def _compute_balance(self):
        for record in self:
            transactions = self.env["openstack.credit.transaction"].search(
                [("credit", "=", record.id)]
            )
            if not transactions:
                record.current_balance = record.initial_balance
                continue
            record.current_balance = record.initial_balance + sum(
                [t.value for t in transactions]
            )

    @api.constrains("start_date", "expiry_date")
    def _check_expiry_date(self):
        """Constrain start date

        Start date must always be before the expiry date.
        """
        if self.expiry_date and self.start_date > self.expiry_date:
            raise exceptions.ValidationError(
                _("Expiry date must be after the start date")
            )

    @property
    def is_active(self):
        """Return whether this credit has started and not expired"""
        if date.today() < self.start_date:
            return False
        return self.expiry_date is None or date.today() < self.expiry_date

    @property
    def available_balance(self):
        """Return current balance or 0.0 if the credit is not active

        That is, if the credit has not yet started or has expired.
        """
        if not self.is_active:
            return 0.0
        else:
            return self.current_balance


class OpenStackCreditTransaction(models.Model):
    """Credit transaction attached to Credit instances"""

    _name = "openstack.credit.transaction"
    _description = "OpenStack Credit Transaction"

    credit = fields.Many2one(
        comodel_name="openstack.credit",
        string="Credit",
        required=True,
    )
    description = fields.Char(string="Description")
    value = fields.Float(string="Value", required=True)

    @api.constrains("credit", "value")
    def _check_value(self):
        """Constraint value

        Current balance on credit can never go below zero.
        """
        transactions = self.env["openstack.credit.transaction"].search(
            [("credit", "=", self.credit.id), ("id", "!=", self.id)]
        )
        if not transactions:
            return

        current_balance = self.credit.initial_balance + sum(
            [t.value for t in transactions]
        )
        if (current_balance + self.value) < 0:
            if abs(current_balance + self.value) < 0.01:
                # If the diff is this small, just make it zero.
                self.value = -current_balance
            else:
                raise exceptions.ValidationError(
                    _("Cannot add transaction that brings balance below zero.")
                )


class OpenStackCreditType(models.Model):
    """Credit types attached to each Credit instance"""

    _name = "openstack.credit.type"
    _description = "OpenStack Credit Type"

    name = fields.Char(string="Name", required=True)
    refundable = fields.Boolean(string="Refundable", default=False)

    product = fields.Many2one(
        comodel_name="product.product", string="Product", required=True
    )
    credits = fields.One2many(
        comodel_name="openstack.credit", inverse_name="credit_type"
    )

    only_for_products = fields.Many2many(
        "product.product",
        string="Only for these products",
        help=(
            "This credit type can only apply to these products. "
            "This is mutually inclusive with `only_for_product_categories`."
        ),
    )

    only_for_product_categories = fields.Many2many(
        "product.category",
        string="Only for these product categories",
        help=(
            "This credit type can only apply to these product categories. "
            "This is mutually inclusive with `only_for_products`."
        ),
    )
