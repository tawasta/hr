from odoo import fields, models


class EmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    cumulative_balance = fields.Float(
        compute="_compute_cumulative_balance",
        help="All timesheet hour balances combined. Counts only confirmed timesheets",
    )

    cumulative_balance_start = fields.Date(
        "Cumulative Balance Start Date",
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
                domain.append(("date_start", ">=", record.cumulative_balance_start))

            timesheets = self.env["hr_timesheet.sheet"].search(domain)
            record.cumulative_balance = sum(timesheets.mapped("total_balance"))
