# -*- coding: utf-8 -*-
from openerp import models, api, fields


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    group_sales = fields.Selection(selection='get_group_sales')

    def get_group_sales(self):
        group = [('a', 'A')]

        if self.user_id:
            group = self.user_id

        return group
