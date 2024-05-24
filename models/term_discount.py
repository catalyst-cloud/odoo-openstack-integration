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


class OpenStackTermDiscount(models.Model):
    """OpenStack Term Discount which is attached to a Partner or project."""

    _name = "openstack.term_discount"
    _description = "OpenStack Term Discount"
    _rec_name = "project"

    partner = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
    )

    project = fields.Many2one(
        comodel_name="openstack.project",
        string="Project",
    )

    start_date = fields.Date(
        string="Start Date",
        required=True,
        default=date.today(),
    )
    end_date = fields.Date(
        string="Expiry Date",
        required=True,
    )
    early_termination_date = fields.Date(string="Early termination Date")

    min_commit = fields.Float(
        string="Minimum Commitment",
        required=True,
    )

    discount_percent = fields.Float(
        string="Discount percentage (0 to 100)",
        required=True,
    )

    superseded_by = fields.Many2one(
        comodel_name="openstack.term_discount",
        string="Superseded by",
    )

    @api.constrains("discount_percent")
    def _check_discount_percent(self):
        """Constrain discount to 0-100"""
        if self.discount_percent < 0.0 or self.discount_percent > 100.0:
            raise exceptions.ValidationError(
                _("discount_percent must be between 0-100")
            )

    @api.constrains("start_date", "end_date")
    def _check_end_date(self):
        """Constrain start date

        Start date must always be before the expiry date.
        """
        if self.end_date and self.start_date > self.end_date:
            raise exceptions.ValidationError(_("End date must be after the start date"))
