from odoo import fields, models


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    def _prepare_bills_vals(self):
        res = super()._prepare_bills_vals()

        today = fields.Date.today()
        self.accounting_date = today
        res["date"] = today
        res["invoice_date"] = today

        return res
