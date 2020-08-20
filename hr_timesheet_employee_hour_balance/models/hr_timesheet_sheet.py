from odoo import api
from odoo import fields
from odoo import models


class HrTimesheetSheet(models.Model):

    _inherit = "hr_timesheet.sheet"

    calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        compute="_compute_calendar_id",
        store=True,
        readonly=False,
    )

    total_hours = fields.Float(related="calendar_id.total_hours", readonly=True)

    total_remaining = fields.Float(
        string="Remaining", compute="_compute_total_remaining", store=True
    )

    cumulative_remaining = fields.Float(
        string="Cumulative Remaining", compute="_compute_cumulative_remaining",
    )

    @api.onchange("employee_id")
    @api.depends("employee_id")
    def _compute_calendar_id(self):
        for record in self:
            if record.employee_id:
                record.calendar_id = record.employee_id.resource_calendar_id

    @api.depends("timesheet_ids.unit_amount", "calendar_id")
    def _compute_total_remaining(self):
        for record in self:
            if record.calendar_id:
                record.total_remaining = record.total_time - record.total_hours

    def _compute_cumulative_remaining(self):
        for record in self:
            timesheets = self.search(
                [
                    ("employee_id", "=", record.employee_id.id),
                    ("date_end", "<=", record.date_end),
                    ("date_end", "<=", record.date_end),
                ]
            )
            record.cumulative_remaining = sum(timesheets.mapped("total_remaining"))
