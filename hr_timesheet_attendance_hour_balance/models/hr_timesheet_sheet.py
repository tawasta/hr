from odoo import api
from odoo import fields
from odoo import models


class HrTimesheetSheet(models.Model):

    _inherit = "hr_timesheet.sheet"

    total_attendance_balance = fields.Float(
        string="Attendance balance", compute="_compute_total_attendance_balance",
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

            timesheets = self.search(domain)
            record.cumulative_attendance_balance = sum(
                timesheets.mapped("total_attendance_balance")
            )
