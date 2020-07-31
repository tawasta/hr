from odoo import api
from odoo import fields
from odoo import models


class HrTimesheetSheet(models.Model):

    _inherit = "hr_timesheet.sheet"

    total_attendance_balance = fields.Float(
        string="Attendance balance",
        compute="_compute_total_attendance_balance",
        store=True,
    )

    @api.depends("timesheet_ids.unit_amount", "calendar_id")
    def _compute_total_attendance_balance(self):
        for record in self:
            if record.total_attendance and record.total_hours:
                record.total_attendance_balance = (
                    record.total_attendance - record.total_hours
                )
