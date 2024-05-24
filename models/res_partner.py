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

from odoo import fields, models


class ResPartner(models.Model):
    """Add some fields related to OpenStack"""

    _inherit = "res.partner"

    stripe_customer_id = fields.Char(
        string="Stripe Customer ID",
        copy=False,
        groups="openstack_integration.group_openstack_user,"
        "openstack_integration.group_openstack_manager",
    )
    os_projects = fields.One2many(
        comodel_name="openstack.project",
        inverse_name="owner",
        copy=False,
        groups="openstack_integration.group_openstack_user,"
        "openstack_integration.group_openstack_manager",
    )
    os_project_contacts = fields.One2many(
        comodel_name="openstack.project_contact",
        inverse_name="partner",
        copy=False,
        groups="openstack_integration.group_openstack_user,"
        "openstack_integration.group_openstack_manager",
    )
    os_customer_group = fields.Many2one(
        comodel_name="openstack.customer_group",
        string="OpenStack Customer Group",
        copy=False,
        groups="openstack_integration.group_openstack_user,"
        "openstack_integration.group_openstack_manager",
    )
    os_reseller = fields.Many2one(
        comodel_name="openstack.reseller",
        string="OpenStack Reseller",
        copy=False,
        groups="openstack_integration.group_openstack_user,"
        "openstack_integration.group_openstack_manager",
    )
    os_trial = fields.Many2one(
        comodel_name="openstack.trial",
        string="OpenStack trial on signup.",
        copy=False,
        groups="openstack_integration.group_openstack_user,"
        "openstack_integration.group_openstack_manager",
    )
    os_referral = fields.Many2one(
        comodel_name="openstack.referral_code",
        string="OpenStack referral on signup.",
        copy=False,
        groups="openstack_integration.group_openstack_user,"
        "openstack_integration.group_openstack_manager",
    )
    os_referral_codes = fields.One2many(
        comodel_name="openstack.referral_code",
        inverse_name="partner",
        string="OpenStack Referral codes",
        copy=False,
        groups="openstack_integration.group_openstack_user,"
        "openstack_integration.group_openstack_manager",
    )
    os_is_cloud_framework_agreement_partner = fields.Boolean(
        string="CFA partner",
        default=False,
        required=False,
        groups=(
            "openstack_integration.group_openstack_user,"
            "openstack_integration.group_openstack_manager"
        ),
    )
