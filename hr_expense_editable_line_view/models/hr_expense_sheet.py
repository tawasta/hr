# -*- coding: utf-8 -*-


from odoo import api, fields, models


class HrExpenseSheet(models.Model):

    _inherit = 'hr.expense.sheet'

    state = fields.Selection(selection=[
        ('draft', 'To Submit'),
        ('submit', 'Submitted'),
        ('approve', 'Approved'),
        ('post', 'Posted'),
        ('done', 'Paid'),
        ('cancel', 'Refused'),
        ],
        default='draft',
        )

    @api.multi
    def reset_expense_sheets(self):
        res = super(HrExpenseSheet, self).reset_expense_sheets()
        self.write({'state': 'draft'})
        for line in self.expense_line_ids:
            line.write({'state': 'draft'})
        return res

    @api.multi
    def submit_expenses(self):
        return self.write({'state': 'submit'})
