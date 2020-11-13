from odoo import api
from odoo import fields
from odoo import models


class HrTimesheetSheet(models.Model):

    _inherit = "hr_timesheet_sheet.sheet"

    calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        compute="_compute_calendar_id",
        store=True,
        readonly=False,
    )

    total_hours = fields.Float(related="calendar_id.total_hours", readonly=True)

    total_balance = fields.Float(
        string="Balance",
        compute="_compute_total_balance",
        help="Current timesheet hour balance",
    )

    cumulative_balance = fields.Float(
        string="Cumulative Balance",
        compute="_compute_cumulative_balance",
        help="All timesheets hour balance. "
        "Counts confirmed timesheets and current timesheet",
    )

    @api.onchange("employee_id")
    @api.depends("employee_id")
    def _compute_calendar_id(self):
        for record in self:
            if record.employee_id:
                record.calendar_id = record.employee_id.resource_calendar_id

    @api.depends("timesheet_ids.unit_amount", "calendar_id")
    def _compute_total_balance(self):
        for record in self:
            if record.calendar_id:
                record.total_balance = record.total_time - record.total_hours

    def _compute_cumulative_balance(self):
        for record in self:
            domain = [
                ("employee_id", "=", record.employee_id.id),
                ("date_end", "<=", record.date_end),
                "|",
                ("state", "=", "done"),
                # Show current draft timesheet balance
                ("id", "=", record.id),
            ]

            if record.employee_id.cumulative_balance_start:
                if record.date_start < record.employee_id.cumulative_balance_start:
                    # No cumulative balance if balance start date is after this timesheet
                    record.cumulative_balance = 0

                domain.append(
                    ("date_start", ">=", record.employee_id.cumulative_balance_start)
                )

            timesheets = self.search(domain)
            record.cumulative_balance = sum(timesheets.mapped("total_balance"))
