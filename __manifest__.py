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

{
    "name": "OpenStack Integration",
    "category": "Tools",
    "summary": """OpenStack integration for the Odoo ERP.""",
    "version": "14.0.1.0.0",
    "author": "Catalyst Cloud",
    "website": "https://catalystcloud.nz",
    "license": "Other OSI approved licence",
    "depends": [
        "account",
        "base",
        "product",
        "report_csv",
        "sale",
    ],
    "data": [
        "report/openstack_invoice_csv.xml",
        "security/openstack_security.xml",
        "security/ir.model.access.csv",
        "views/main_menu.xml",
        "views/account_move_view.xml",
        "views/credit_view.xml",
        "views/customer_group_view.xml",
        "views/grant_view.xml",
        "views/project_view.xml",
        "views/referral_view.xml",
        "views/report_invoice.xml",
        "views/reseller_view.xml",
        "views/res_partner_view.xml",
        "views/sale_order_view.xml",
        "views/support_subscription_view.xml",
        "views/term_discount_view.xml",
        "views/trial_view.xml",
        "views/volume_discount_view.xml",
        "views/voucher_code_view.xml",
        # load mail template after report_invoice.xml which it refers to
        "data/mail_template_data.xml",
    ],
    "installable": True,
}
