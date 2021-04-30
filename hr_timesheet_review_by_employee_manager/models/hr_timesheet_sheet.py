##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2021- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import fields, models, api, SUPERUSER_ID

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class Sheet(models.Model):

    # 1. Private attributes
    _inherit = 'hr_timesheet.sheet'

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.multi
    def _get_possible_reviewers(self):
        self.ensure_one()
        res = self.env['res.users'].browse(SUPERUSER_ID)
        if self.review_policy == 'hr':
            res |= self.env.ref('hr.group_hr_user').users
        elif self.review_policy == 'hr_manager':
            res |= self.env.ref('hr.group_hr_manager').users
        elif self.review_policy == 'timesheet_manager':
            res |= self.env.ref('hr_timesheet.group_timesheet_manager').users
        elif self.review_policy == 'employee_manager':
            if self.employee_id.parent_id.user_id:
                res |= self.employee_id.parent_id.user_id
        return res

    # 7. Action methods

    # 8. Business methods
