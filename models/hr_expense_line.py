# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from openerp import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class HrExpenseLine(models.Model):
    
    # 1. Private attributes
    _inherit = 'hr.expense.line'

    # 2. Fields declaration
    employee = fields.Many2one(
        'hr.employee',
        "Employee",
        readonly=True,
        compute='_get_employee',
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.one
    def _get_employee(self):
        self.employee = self.expense_id.employee_id

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
