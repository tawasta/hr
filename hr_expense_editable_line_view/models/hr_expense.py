# -*- coding: utf-8 -*-


from odoo import api, models


class HrExpense(models.Model):

    _inherit = 'hr.expense'

    @api.depends('sheet_id', 'sheet_id.account_move_id', 'sheet_id.state')
    def _compute_state(self):
        for expense in self:
            if not expense.sheet_id:
                expense.state = "draft"
            elif expense.sheet_id.state == "draft":
                expense.state = "draft"
            elif expense.sheet_id.state == "cancel":
                expense.state = "refused"
            elif expense.sheet_id.state == "submit":
                expense.state = "reported"
            else:
                expense.state = "done"
