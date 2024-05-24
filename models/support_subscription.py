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


class OpenStackSupportSubscription(models.Model):
    """An openstack support subscription

    Attached to a partner or optionally a project."""

    _name = "openstack.support_subscription"
    _description = "OpenStack Support Subscription"
    _rec_name = "project"

    project = fields.Many2one(
        comodel_name="openstack.project",
        string="Project",
    )

    partner = fields.Many2one(
        "res.partner",
        string="Partner",
    )

    billing_type = fields.Selection(
        selection=[
            ("paid", "paid"),
            ("complimentary", "complimentary"),
        ],
        default="paid",
        string="Billing Type",
        required=True,
    )

    start_date = fields.Date(
        string="Start Date",
        required=True,
        default=date.today(),
    )
    end_date = fields.Date(string="End Date")
    support_subscription_type = fields.Many2one(
        comodel_name="openstack.support_subscription.type",
        string="Subscription Type",
        required=True,
    )

    @api.constrains("project", "")
    def _check_owner(self):
        """Check an owner is set

        Project and/or Partner must be set
        """
        if not self.project and not self.partner:
            raise exceptions.ValidationError(
                _("Must set at one or both Project/Partner.")
            )

    @api.constrains("start_date", "end_date")
    def _check_end_date(self):
        """Constrain start date

        Start date must always be before the expiry date.
        """
        if self.end_date and self.start_date > self.end_date:
            raise exceptions.ValidationError(_("End date must be after the start date"))


class OpenStackSupportSubscriptionType(models.Model):
    """Support Subscription type."""

    _name = "openstack.support_subscription.type"
    _description = "OpenStack Support Subscription Type"

    name = fields.Char(string="Name", required=True)
    product = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
    )
    usage_percent = fields.Float(
        string="Percentage of usage to compare to price (0 to 100)",
        required=True,
    )

    support_subscription = fields.One2many(
        comodel_name="openstack.support_subscription",
        inverse_name="support_subscription_type",
    )

    @api.constrains("discount_percent")
    def _check_discount_percent(self):
        """Constrain discount to 0-100"""
        if self.discount_percent < 0.0 or self.discount_percent > 100.0:
            raise exceptions.ValidationError(
                _("discount_percent must be between 0-100")
            )
