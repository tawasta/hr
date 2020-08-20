from odoo import models, fields


class Employee(models.Model):

    _inherit = "hr.employee"

    hour_balance_start = fields.Date(
        string="Hour Balance Start Date",
        help=(
            "Date from which onwards the hour balance is calculated. Set "
            "this as the date when the user started filling out timesheets."
        ),
    )
