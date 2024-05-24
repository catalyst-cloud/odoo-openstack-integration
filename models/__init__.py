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

from . import account_move
from . import credit
from . import customer_group
from . import grant
from . import project
from . import referral
from . import reseller
from . import res_partner
from . import sale_order
from . import support_subscription
from . import term_discount
from . import trial
from . import volume_discount
from . import voucher_codes

__all__ = [
    "account_move",
    "credit",
    "customer_group",
    "grant",
    "project",
    "referral",
    "reseller",
    "res_partner",
    "sale_order",
    "support_subscription",
    "term_discount",
    "trial",
    "volume_discount",
    "voucher_codes",
]
