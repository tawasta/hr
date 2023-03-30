from odoo import api, fields, models


class HrTimesheetSheet(models.Model):

    _inherit = "hr_timesheet.sheet"

    total_attendance_balance = fields.Float(
        string="Attendance balance",
        compute="_compute_total_attendance_balance",
    )

    cumulative_attendance_balance = fields.Float(
        string="Cumulative Attendance",
        compute="_compute_cumulative_attendance_balance",
    )

    @api.depends("timesheet_ids.unit_amount", "calendar_id")
    def _compute_total_attendance_balance(self):
        for record in self:
            if record.total_attendance and record.total_hours:
                record.total_attendance_balance = (
                    record.total_attendance - record.total_hours
                )
            else:
                record.total_attendance_balance = 0

    def _compute_cumulative_attendance_balance(self):
        for record in self:
            domain = [
                ("employee_id", "=", record.employee_id.id),
                ("date_end", "<=", record.date_end),
                # Count only done timesheets?
                # "|",
                # ("state", "=", "done"),
                # Show current draft timesheet balance
                # ("id", "=", record.id),
            ]

            if record.employee_id.cumulative_balance_start:
                if record.date_start < record.employee_id.cumulative_balance_start:
                    # No cumulative balance if balance start date is after this timesheet
                    record.cumulative_balance = 0

                domain.append(
                    ("date_start", ">=", record.employee_id.cumulative_balance_start)
                )

            timesheets = self.search(domain)
            record.cumulative_attendance_balance = sum(
                timesheets.mapped("total_attendance_balance")
            )
