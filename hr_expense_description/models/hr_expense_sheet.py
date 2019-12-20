# -*- coding: utf-8 -*-


from odoo import fields, models


class HrExpenseSheet(models.Model):

    _inherit = 'hr.expense.sheet'

    expense_description = fields.Text(
        string='Expense details',
    )
