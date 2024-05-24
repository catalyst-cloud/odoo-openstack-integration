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


class OpenStackGrant(models.Model):
    """OpenStack grant which is attached to a project"""

    _name = "openstack.grant"
    _description = "Cloud Grant"

    voucher_code = fields.Many2one(
        comodel_name="openstack.voucher_code",
        string="Voucher Code",
    )

    project = fields.Many2one(
        comodel_name="openstack.project",
        string="Project",
        required=True,
    )

    @api.depends("project", "voucher_code")
    def _get_name(self):
        """Computed field to show in the breadcrumbs"""
        for grant in self:
            name = grant.project.name
            if grant.voucher_code:
                name = f"{grant.project.name} - {grant.voucher_code.name}"
            grant.name = name

    name = fields.Char(string="Name", compute="_get_name")

    grant_type = fields.Many2one(
        comodel_name="openstack.grant.type",
        string="Grant Type",
        required=True,
    )

    start_date = fields.Date(string="Start Date", required=True, default=date.today())
    expiry_date = fields.Date(string="Expiry Date")

    value = fields.Float(string="Value", required=True)

    @api.constrains("start_date", "expiry_date")
    def _check_expiry_date(self):
        """Constrain start date

        Start date must always be before the expiry date.
        """
        if self.expiry_date and self.start_date > self.expiry_date:
            raise exceptions.ValidationError(
                _("Expiry date must be after the start date")
            )

    @api.constrains("value")
    def _check_value_is_positive(self):
        """Constrain value"""
        if self.value < 0.0:
            raise exceptions.ValidationError(_("value cannot be negative"))

    def is_active(self, today=None):
        """Return whether this grant has started and not expired"""
        if today is None:
            today = date.today()
        if today < self.start_date:
            return False
        return self.expiry_date is None or today < self.expiry_date


class OpenStackGrantType(models.Model):
    """Grant types attached to each grant instance"""

    _name = "openstack.grant.type"
    _description = "OpenStack Grant Type"

    name = fields.Char(string="Name", required=True)
    product = fields.Many2one(
        comodel_name="product.product", string="Product", required=True
    )
    grants = fields.One2many(comodel_name="openstack.grant", inverse_name="grant_type")

    only_on_group_root = fields.Boolean(
        string="Only on group root",
        help=(
            "If true, this grant type is only allowed to be part of an invoice "
            "grouping if it is on the group root project."
        ),
        default=False,
    )

    only_for_products = fields.Many2many(
        "product.product",
        string="Only for these products",
        help=(
            "This grant type can only apply to these products. "
            "This is mutually inclusive with `only_for_product_categories`."
        ),
    )

    only_for_product_categories = fields.Many2many(
        "product.category",
        string="Only for these product categories",
        help=(
            "This grant type can only apply to these product categories. "
            "This is mutually inclusive with `only_for_products`."
        ),
    )
