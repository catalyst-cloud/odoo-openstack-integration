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


class OpenStackVolumeDiscountRange(models.Model):
    """OpenStack Volume Discount ranges"""

    _name = "openstack.volume_discount_range"
    _description = "OpenStack Volume Discount Range"

    customer_group = fields.Many2one(
        "openstack.customer_group",
        "Customer Group",
    )

    @api.depends("use_max", "min", "max", "customer_group")
    def _get_name(self):
        """Computed field to show in the breadcrumbs"""
        for vol_disc in self:
            if vol_disc.use_max:
                name = f"{vol_disc.min} to {vol_disc.max}"
            else:
                name = f"{vol_disc.min} and higher"
            if vol_disc.customer_group:
                name += f" {vol_disc.customer_group.name}"
            vol_disc.name = name

    name = fields.Char(string="Name", compute="_get_name")

    min = fields.Float(string="min end of the range", required=True)

    use_max = fields.Boolean(string="Use max", default=True)
    max = fields.Float(
        string="Max end of the range",
        default=None,
    )

    discount_percent = fields.Float(
        "Discount percentage for this range (0-100)", required=True
    )

    @api.constrains("discount_percent")
    def _check_discount_percent(self):
        """Constrain discount to 0-100"""
        if self.discount_percent < 0.0 or self.discount_percent > 100.0:
            raise exceptions.ValidationError(
                _("discount_percent must be between 0-100")
            )

    @api.constrains("min", "max")
    def _check_max(self):
        """Min must be less than max."""
        if self.max and self.min > self.max:
            raise exceptions.ValidationError(_("Min must be less than max."))
