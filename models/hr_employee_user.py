# -*- coding: utf-8 -*-
from openerp import models, fields


class HrEmployeeUser(models.Model):

    _inherit = 'hr.employee'

    ''' USER RELATION '''
    user_state = fields.Char(
        compute='get_user_state',
        readonly=True
    )

    ''' SALES '''
    show_group_sales = fields.Boolean(
        compute='compute_show_group_sales',
    )
    group_sales = fields.Selection(
        selection='get_group_sales',
        inverse='set_group_sales',
        string='Sales',
        default='user',
        help='SALES PERMISSIONS' + '\n\n' +
        'User' + '\n' +
        'Leads, opportunities, sales, partners and calls.' + '\n\n' +
        'Manager' + '\n' +
        'Leads, opportunities, sales, partners, calls, products,' + ' \n' +
        'categories, packaging, pricelists, etc.'
    )

    ''' PURCHASES '''
    show_group_purchase = fields.Boolean(
        compute='compute_show_group_purchase',
    )
    group_purchase = fields.Selection(
        selection='get_group_purchase',
        inverse='set_group_purchase',
        string='Purchases',
        default='user',
    )

    ''' PROJECT '''
    show_group_project = fields.Boolean(
        compute='compute_show_group_project',
    )
    group_project = fields.Selection(
        selection='get_group_project',
        inverse='set_group_project',
        string='Projects',
        default='user',
    )

    ''' ACCOUNT '''
    show_group_account = fields.Boolean(
        compute='compute_show_group_account',
    )
    group_account = fields.Selection(
        selection='get_group_account',
        inverse='set_group_account',
        string='Finance',
        default='invoicing',
    )

    ''' HR '''
    show_group_hr = fields.Boolean(
        compute='compute_show_group_hr',
    )
    group_hr = fields.Selection(
        selection='get_group_hr',
        inverse='set_group_hr',
        string='Human relations',
        default='employee',
        required=True,
    )

    ''' STOCK '''
    show_group_stock = fields.Boolean(
        compute='compute_show_group_stock',
    )
    group_stock = fields.Selection(
        selection='get_group_stock',
        inverse='set_group_stock',
        string='Warehouse',
        default='user',
    )

    ''' User creation '''
    def create_user(self, vals):
        users_object = self.env['res.users']

        user_vals = {
            'login': vals['work_email'],
            'name': vals['name'],
            # 'groups_id': {(6, False, self.get_default_groups())}
        }

        user_id = users_object.sudo().create(user_vals)

        vals['user_id'] = user_id.id
        vals['address_home_id'] = user_id.partner_id.id

        user_id.partner_id.email = vals['work_email']
        user_id.partner_id.phone = vals['mobile_phone']

        return vals

    def get_user_state(self):
        self.user_state = ('active' if self.user_id.login_date else 'new')

    ''' SALES '''
    def get_group_sales(self):
        group = [
            ('user', 'User'),
            ('manager', 'Manager'),
        ]

        return group

    def set_group_sales(self):
        category_name = "Sales"

        if not self.group_sales:
            group = False

        elif self.group_sales == 'user':
            group = self.get_group_by_name("See all Leads", category_name)

        elif self.group_sales == 'manager':
            group = self.get_group_by_name("Manager", category_name)

        current_groups = self.get_groups_by_category_name(category_name)

        ''' Unset current groups '''
        for current_group in current_groups:
            self.sudo().user_id.groups_id = [(3, current_group.id)]

        ''' Set the new group '''
        if group:
            self.sudo().user_id.groups_id = [(4, group.id)]

    ''' PURCHASES '''
    def get_group_purchase(self):
        group = [
            ('user', 'User'),
            ('manager', 'Manager'),
        ]

        return group

    def set_group_purchase(self):
        category_name = "Purchases"

        if not self.group_purchase:
            group = False

        elif self.group_purchase == 'user':
            group = self.get_group_by_name("User", category_name)

        elif self.group_purchase == 'manager':
            group = self.get_group_by_name("Manager", category_name)

        current_groups = self.get_groups_by_category_name(category_name)

        ''' Unset current groups '''
        for current_group in current_groups:
            self.sudo().user_id.groups_id = [(3, current_group.id)]

        ''' Set the new group '''
        if group:
            self.sudo().user_id.groups_id = [(4, group.id)]

    ''' PROJECT '''
    def get_group_project(self):
        group = [
            ('user', 'User'),
            ('manager', 'Manager'),
        ]

        return group

    def set_group_project(self):
        category_name = "Project"

        if not self.group_project:
            group = False

        elif self.group_project == 'user':
            group = self.get_group_by_name("User", category_name)

        elif self.group_project == 'manager':
            group = self.get_group_by_name("Manager", category_name)

        current_groups = self.get_groups_by_category_name(category_name)

        ''' Unset current groups '''
        for current_group in current_groups:
            self.sudo().user_id.groups_id = [(3, current_group.id)]

        ''' Set the new group '''
        if group:
            self.sudo().user_id.groups_id = [(4, group.id)]

    ''' ACCOUNT '''
    def get_group_account(self):
        group = [
            ('view', 'View'),
            ('invoicing', 'Invoicing'),
            ('accountant', 'Accountant'),
            ('manager', 'Manager'),
        ]

        return group

    def set_group_account(self):
        category_name = "Accounting"

        if not self.group_account:
            group = False

        elif self.group_account == 'view':
            group = self.get_group_by_name("Can view", category_name)

        elif self.group_account == 'invoicing':
            group = self.get_group_by_name("Invoicing", category_name)

        elif self.group_account == 'accountant':
            group = self.get_group_by_name("Accountant", category_name)

        elif self.group_account == 'manager':
            group = self.get_group_by_name("Financial Manager", category_name)

        current_groups = self.get_groups_by_category_name(category_name)

        ''' Unset current groups '''
        for current_group in current_groups:
            self.sudo().user_id.groups_id = [(3, current_group.id)]

        ''' Set the new group '''
        if group:
            self.sudo().user_id.groups_id = [(4, group.id)]

    ''' HUMAN RESOURCES '''
    def get_group_hr(self):
        group = [
            ('employee', 'Employee'),
            ('officer', 'Officer'),
            ('manager', 'Manager'),
        ]

        return group

    def set_group_hr(self):
        category_name = "Human Resources"

        if not self.group_hr:
            group = False

        elif self.group_hr == 'employee':
            group = self.get_group_by_name("Employee", category_name)

        elif self.group_hr == 'officer':
            group = self.get_group_by_name("Officer", category_name)

        elif self.group_hr == 'manager':
            group = self.get_group_by_name("Manager", category_name)

        current_groups = self.get_groups_by_category_name(category_name)

        ''' Unset current groups '''
        for current_group in current_groups:
            self.sudo().user_id.groups_id = [(3, current_group.id)]

        ''' Set the new group '''
        if group:
            self.sudo().user_id.groups_id = [(4, group.id)]

    ''' WAREHOUSE / STOCK '''
    def get_group_stock(self):
        group = [
            ('user', 'User'),
            ('manager', 'Manager'),
        ]

        return group

    def set_group_stock(self):
        category_name = "Warehouse"

        if not self.group_stock:
            group = False

        elif self.group_hr == 'user':
            group = self.get_group_by_name("User", category_name)

        elif self.group_hr == 'manager':
            group = self.get_group_by_name("Manager", category_name)

        current_groups = self.get_groups_by_category_name(category_name)

        ''' Unset current groups '''
        for current_group in current_groups:
            self.sudo().user_id.groups_id = [(3, current_group.id)]

        ''' Set the new group '''
        if group:
            self.sudo().user_id.groups_id = [(4, group.id)]
