from odoo import fields, models


class HrExpense(models.Model):

    _inherit = "hr.expense"

    def _prepare_move_values(self):
        """
        Override accounting date to be the posting date
        """
        move_values = super()._prepare_move_values()

        move_values["date"] = fields.Date.today()

        return move_values
