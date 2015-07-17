# -*- coding: utf-8 -*-
from openerp import models, api, fields

import logging
_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    group_sales = fields.Selection(
        selection='get_group_sales',
        inverse='set_group_sales',
        string='Sales group'
    )

    @api.onchange('name')
    def onchange_name(self):
        pass
        # manager_group = self.get_group_by_name("Manager", "Sales")

    @api.model
    def create(self, vals):
        ''' Creates an user and sets default permission rights '''

        if not self.user_id:
            users_object = self.env['res.users']

            user_vals = {
                'login': vals['work_email'],
                'name': vals['name'],
            }

            user_id = users_object.sudo().create(user_vals)

            vals['user_id'] = user_id.id
            vals['address_home_id'] = user_id.partner_id.id

        return super(HrEmployee, self).create(vals)

    def get_group_sales(self):
        group = [
            ('salesperson', 'Sales person'),
            ('salesmanager', 'Sales manager'),
        ]

        return group

    def set_group_sales(self):
        if self.group_sales == 'salesperson':
            pass

        elif self.group_sales == 'salesmanager':
            pass

    def get_group_by_name(self, group_name, category_name):
        # Gets security group by group name
        groups_obj = self.env['res.groups']

        groups = self.get_groups_by_category_name(category_name)

        group = groups_obj.search([('name', '=', group_name),
                                   ('category_id', 'in', groups.ids)])

        return group

    def get_groups_by_category_name(self, category_name):
        # Gets security groups by category name

        groups_obj = self.env['res.groups']

        groups = groups_obj.search([('category_id.name', '=', category_name)])

        return groups
