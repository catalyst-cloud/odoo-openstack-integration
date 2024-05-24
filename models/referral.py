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


class OpenStackReferralCode(models.Model):
    _name = "openstack.referral_code"
    _description = "OpenStack referral code."

    partner = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
    )
    code = fields.Char("Code", required=True, unique=True)

    @api.depends("partner", "code")
    def _get_name(self):
        """Computed field to show in the breadcrumbs"""
        for ref in self:
            ref.name = f"{ref.partner.name} - {ref.code}"

    name = fields.Char("Name", compute="_get_name")

    referral_credit_amount = fields.Float(
        string="Referral credit initial balance",
    )
    referral_credit_type = fields.Many2one(
        comodel_name="openstack.credit.type",
        string="Referral credit Type",
        required=True,
    )
    referral_credit_duration = fields.Integer(
        string="Referral credit duration in days",
        required=True,
    )

    before_reward_usage_threshold = fields.Float(
        string="Before reward usage threshold",
        required=True,
    )

    reward_credit_amount = fields.Float(
        string="Reward credit initial balance",
        required=True,
    )
    reward_credit_type = fields.Many2one(
        comodel_name="openstack.credit.type",
        string="Reward credit Type",
        required=True,
    )
    reward_credit_duration = fields.Integer(
        string="Reward credit duration in days",
        required=True,
    )

    allowed_uses = fields.Integer(
        string="Number of allowed uses of this code. Default: -1 (infinite)",
        default=-1,
        required=True,
    )

    referrals = fields.One2many(
        comodel_name="res.partner",
        inverse_name="os_referral",
        string="Referrals using this code.",
    )
