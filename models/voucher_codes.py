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


class OpenStackVoucherCode(models.Model):
    """OpenStack voucher code."""

    _name = "openstack.voucher_code"
    _description = "OpenStack Voucher Code"

    code = fields.Char(string="Code", required=True, unique=True)

    @api.depends("code")
    def _get_name(self):
        """Computed field to show field 'code' in the breadcrumbs"""
        for voucher in self:
            voucher.name = voucher.code

    name = fields.Char(string="Name", compute="_get_name")

    claimed = fields.Boolean(string="Claimed", default=False)
    multi_use = fields.Boolean(string="Multi-use code", default=False)

    expiry_date = fields.Date(string="Expiry Date")

    sales_person = fields.Many2one(
        comodel_name="res.partner",
        string="Sales person",
    )

    customer_group = fields.Many2one(
        comodel_name="openstack.customer_group",
        string="Customer Group",
    )

    credit_amount = fields.Float(
        string="Credit initial balance",
    )
    credit_type = fields.Many2one(
        comodel_name="openstack.credit.type",
        string="Credit Type",
    )
    credit_duration = fields.Integer(
        string="Credit duration in days",
    )

    grant_value = fields.Float(
        string="Grant value",
    )
    grant_type = fields.Many2one(
        comodel_name="openstack.grant.type",
        string="Grant Type",
    )
    grant_duration = fields.Integer(
        string="Grant duration in days",
    )

    quota_size = fields.Char(string="Default quota size on signup")

    tags = fields.Many2many(
        "res.partner.category",
        column1="openstack_voucher_id",
        column2="category_id",
        string="Tags",
    )

    @api.constrains("claimed", "multi_use")
    def _check_claimed_if_multi_use(self):
        """Can't be claimed if multi_use"""
        if self.multi_use and self.claimed:
            raise exceptions.ValidationError(_("Can't claim if multi_use is true."))
