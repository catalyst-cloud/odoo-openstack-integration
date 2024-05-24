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

from odoo import _, api, fields, models, exceptions


class OpenStackReseller(models.Model):
    """A customer of OpenStack who has signed as a reseller."""

    _name = "openstack.reseller"
    _description = "OpenStack Reseller "

    partner = fields.Many2one(
        comodel_name="res.partner",
        string="Reseller partner",
        required=True,
    )

    @api.depends("partner")
    def _get_name(self):
        """Computed field to show in the breadcrumbs"""
        for reseller in self:
            reseller.name = reseller.partner.name

    name = fields.Char(string="Name", compute="_get_name")

    tier = fields.Many2one(
        "openstack.reseller.tier",
        "Reseller tier",
        required=True,
    )
    hide_billing = fields.Boolean(
        string="Hide billing",
        default=False,
    )
    alternative_billing_url = fields.Char(
        string="Alternative billing url",
    )
    hide_support = fields.Boolean(
        string="Hide support",
        default=False,
    )
    alternative_support_url = fields.Char(
        string="Alternative support url",
    )

    demo_project = fields.Many2one(
        comodel_name="openstack.project",
        string="Demo tenant",
    )


class OpenStackResellerTier(models.Model):
    _name = "openstack.reseller.tier"
    _description = "Reseller tier"

    name = fields.Char(
        string="Tier name",
        required=True,
    )

    min_usage_threshold = fields.Float(
        string="Required usage amount for tier.",
        required=True,
    )

    discount_percent = fields.Float(
        string="Discount percentage for this range (0 to 100)",
        required=True,
    )
    discount_product = fields.Many2one(
        comodel_name="product.product",
        string="Discount product",
        required=True,
    )

    free_support_hours = fields.Integer(
        string="Free support hours per month",
        required=True,
    )

    free_monthly_credit = fields.Float(
        string="Free monthly demo credit",
        required=True,
    )
    free_monthly_credit_product = fields.Many2one(
        comodel_name="product.product",
        string="Free monthly credit product",
        required=True,
    )

    @api.constrains("discount_percent")
    def _check_discount_percent(self):
        """Constrain discount to 0-100"""
        if self.discount_percent < 0.0 or self.discount_percent > 100.0:
            raise exceptions.ValidationError(
                _("discount_percent must be between 0-100")
            )
