from odoo import models, fields


class Employee(models.Model):

    _inherit = "hr.employee"

    cumulative_balance = fields.Float(
        string="Cumulative Balance",
        compute="_compute_cumulative_balance",
        help="All timesheet hour balances combined. "
        "Counts only confirmed timesheets",
    )

    cumulative_balance_start = fields.Date(
        string="Cumulative Balance Start Date",
        help=(
            "Date from which onwards the hour balance is calculated. Set "
            "this as the date when the user started filling out timesheets."
        ),
    )

    def _compute_cumulative_balance(self):
        for record in self:
            domain = [
                ("employee_id", "=", record.id),
                ("state", "=", "done"),
            ]

            if record.cumulative_balance_start:
                domain.append(("date_from", ">=", record.cumulative_balance_start))

            timesheets = self.env["hr_timesheet_sheet.sheet"].search(domain)
            record.cumulative_balance = sum(timesheets.mapped("total_balance"))
