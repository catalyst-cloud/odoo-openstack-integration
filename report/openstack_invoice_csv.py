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

import csv

from odoo.exceptions import UserError
from odoo import models


class OpenStackInvoiceCSV(models.AbstractModel):
    _name = "report.openstack_integration.openstack_invoice_csv"
    _inherit = "report.report_csv.abstract"
    _description = "OpenStack Invoice CSV"

    def generate_csv_report(self, writer, data, invoice):
        if len(invoice) != 1:
            # TODO: Hey why - can do for more
            raise UserError("This CSV can only be created for one invoice at a time")
        writer.writeheader()
        # TODO: Investigate why this line is needed
        invoice = invoice.with_context(allowed_company_ids=[invoice.company_id.id])
        for line in invoice.invoice_line_ids:
            writer.writerow(
                {
                    "name": line.name,
                    "project": line.os_project.name,
                    "project_id": line.os_project.os_id,
                    "product": line.product_id.name,
                    "region": line.os_region,
                    "resource_name": line.os_resource_name,
                    "resource_type": line.os_resource_type,
                    "resource_id": line.os_resource_id,
                    "unit_type": line.product_id.default_code,
                    "units": line.quantity,
                    "price_per_unit": line.price_unit,
                    "subtotal": round(line.price_subtotal, 6),
                }
            )

    def csv_report_options(self):
        res = super().csv_report_options()
        fieldnames = [
            "name",
            "project",
            "project_id",
            "product",
            "region",
            "resource_name",
            "resource_type",
            "resource_id",
            "unit_type",
            "units",
            "price_per_unit",
            "subtotal",
        ]
        for field in fieldnames:
            res["fieldnames"].append(field)
        res["delimiter"] = ","
        res["quoting"] = csv.QUOTE_NONNUMERIC
        return res
