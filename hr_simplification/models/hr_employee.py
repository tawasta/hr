# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports (One per line sorted and splitted in python stdlib):

# 3. Odoo imports (openerp):
from openerp import api, fields, models

# 4. Imports from Odoo modules (rarely, and only if necessary):

# 5. Local imports in the relative form:

# 6. Unknown third party imports (One per line sorted and splitted in python stdlib):


class HrEmployee(models.Model):
    
    # 1. Private attributes
    _inherit = 'hr.employee'

    # 2. Fields declaration
    show_all = fields.Boolean(
        'Show all fields',
        help="Some of the lesser used fields are hidden by default"
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges
    @api.onchange('name')
    @api.depends('work_email')
    def onchange_name_update_email(self):
        if self.name and not self.work_email:
            # Try to guess the username (email)
            email = self.name.lower()
            email = email.replace(" ", ".")
            email = email.replace('å'.decode('utf-8'), "a")
            email = email.replace('ä'.decode('utf-8'), "a")
            email = email.replace('ö'.decode('utf-8'), "o")

            company_email = self.company_id.email
            if company_email:
                domain = company_email[company_email.find('@'):]
                email += domain

            self.work_email = email

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
