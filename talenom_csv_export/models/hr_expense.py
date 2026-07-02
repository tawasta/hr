from odoo import fields, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    talenom_export = fields.Boolean(
        string="Export to Talenom",
        default=True,
        help="If unchecked, this expense is not included in the Talenom "
        "payroll CSV export.",
    )
    talenom_export_date = fields.Datetime(
        readonly=True,
        copy=False,
        help="Date and time when this expense was included in a Talenom "
        "payroll CSV export. Once set, the expense is not exported again.",
    )
