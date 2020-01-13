# -*- coding: utf-8 -*-
from odoo import api, models, fields


class HrExpense(models.Model):

    _inherit = 'hr.expense'

    @api.multi
    def _prepare_move_values(self):
        """
        Override accounting date to be the posting date
        """
        move_values = super(HrExpense, self)._prepare_move_values()

        move_values['date'] = fields.Date.today()

        return move_values
