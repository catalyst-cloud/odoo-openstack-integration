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


class OpenStackTrial(models.Model):
    _name = "openstack.trial"
    _description = "OpenStack Trial"
    _rec_name = "partner"

    partner = fields.Many2one(
        "res.partner",
        string="Trial partner",
        required=True,
    )

    start_date = fields.Date(
        string="Start Date",
        required=True,
        default=date.today(),
    )
    end_date = fields.Date(string="End Date", required=True)

    account_suspended_on = fields.Date(string="Account suspended date")
    account_terminated_on = fields.Date(string="Account terminated date")

    account_upgraded_on = fields.Date(string="Account upgraded date")

    @api.constrains("start_date", "end_date")
    def _check_end_date(self):
        """Constrain start date

        Start date must always be before the expiry date.
        """
        if self.end_date and self.start_date > self.end_date:
            raise exceptions.ValidationError(_("End date must be after the start date"))
