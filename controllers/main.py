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

import json

from odoo.http import content_disposition, request, route
from odoo.tools.safe_eval import safe_eval, time

from odoo.addons.report_csv.controllers import main as report


class ReportController(report.ReportController):
    """report_csv.ReportController that fixes a mysterious permission problem"""

    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter == "csv":
            report = request.env["ir.actions.report"]._get_report_from_name(reportname)
            context = dict(request.env.context)
            if docids:
                docids = [int(i) for i in docids.split(",")]
            if data.get("options"):
                data.update(json.loads(data.pop("options")))
            if data.get("context"):
                # Ignore 'lang' here, because the context in data is the one
                # from the webclient *but* if the user explicitly wants to
                # change the lang, this mechanism overwrites it.
                data["context"] = json.loads(data["context"])
                if data["context"].get("lang"):
                    del data["context"]["lang"]
                context.update(data["context"])
            # TODO: Investigate why we need to insert sudo() here
            csv = report.sudo().with_context(context)._render_csv(docids, data=data)[0]
            filename = "{}.{}".format(report.name, "csv")
            if docids:
                obj = request.env[report.model].browse(docids)
                if report.print_report_name and not len(obj) > 1:
                    report_name = safe_eval(
                        report.print_report_name,
                        {"object": obj, "time": time, "multi": False},
                    )
                    filename = "{}.{}".format(report_name, "csv")
                # When we print multiple records we still allow a custom
                # filename.
                elif report.print_report_name and len(obj) > 1:
                    report_name = safe_eval(
                        report.print_report_name,
                        {"objects": obj, "time": time, "multi": True},
                    )
                    filename = "{}.{}".format(report_name, "csv")
            csvhttpheaders = [
                ("Content-Type", "text/csv"),
                ("Content-Length", len(csv)),
                ("Content-Disposition", content_disposition(filename)),
            ]
            return request.make_response(csv, headers=csvhttpheaders)
        return super(ReportController, self).report_routes(
            reportname, docids, converter, **data
        )
