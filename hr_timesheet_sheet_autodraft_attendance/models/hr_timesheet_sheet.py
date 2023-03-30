from odoo import fields, models


class HrTimesheetSheet(models.Model):

    _inherit = "hr_timesheet.sheet"

    def cron_auto_create_sheets(self):
        employees = self.env["hr.employee"].search([])
        aal = self.env["account.analytic.line"]

        # Select any aa for dummy record
        aa = self.env["account.analytic.account"].search([], limit=1)

        for employee in employees:
            if not employee.user_id:
                continue

            # Create a dummy analytic line to prevent copying code from autodraft-module
            dummy = aal.create(
                {
                    "name": "tmp",
                    "employee_id": employee.id,
                    "company_id": self.env.user.company_id.id,
                    "date": fields.Date.today(),
                    "account_id": aa.id,
                }
            )

            # Create timesheets if not already created
            sheet = dummy._determine_sheet()

            dummy.unlink()
            return sheet
