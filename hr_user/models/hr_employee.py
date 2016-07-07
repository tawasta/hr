# -*- coding: utf-8 -*-
from openerp import models, api
from openerp import tools
from openerp import exceptions

import re
import logging
_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    ''' Onchanges '''
    @api.onchange('name')
    def onchange_name_update_groups(self):
        groups = []

        groups.append(
            self.get_group_by_name('See all Leads', 'Sales').id or False)
        groups.append(
            self.get_group_by_name('Employee', 'Human Resources').id or False)

    @api.onchange('work_email')
    def onchange_work_email_validate_email(self):
        if self.work_email:
            valid_email = re.match(tools.single_email_re, self.work_email)

            if not valid_email:
                raise exceptions.Warning("Invalid email!")

    ''' Main function overrides '''
    @api.model
    def create(self, values):
        # Creates an user and sets default permission rights

        # Create user
        if 'user_id' not in values or not values['user_id']:
            values = self.create_user(values)

        return super(HrEmployee, self).create(values)

    @api.one
    def write(self, vals):
        if self.user_id and 'work_email' in vals:
            self.sudo().user_id.login = vals['work_email']

        return super(HrEmployee, self).write(vals)

    @api.one
    def unlink(self):

        if self.sudo().user_id:
            self.sudo().user_id.active = False

        super(HrEmployee, self).unlink()
