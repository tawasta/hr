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
        'Leads, opportunities, sales, partners, calls.' + '\n\n' +

        'Manager' + '\n' +
        'All of the above AND' + ' ' +
        'products, categories, packaging, pricelists, reports, etc.'
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

        help='PURCHASES PERMISSIONS' + '\n\n' +
        'User' + '\n' +
        'Purchase orders, warehouse, products' + '\n\n' +

        'Manager' + '\n' +
        'All of the above AND' + ' ' +
        'reports, packaging, pricelists'
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

        help='PROJECT PERMISSIONS' + '\n\n' +
        'User' + '\n' +
        'Tasks, task stages, leaves' + '\n\n' +

        'Manager' + '\n' +
        'All of the above AND' + ' ' +
        'projects, project categories, attendance'
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

        help='FINANCE PERMISSIONS' + '\n\n' +
        'Invoicing' + '\n' +
        'Invoices, reconciliations, accounts, vouchers' + '\n\n' +

        'Accountant' + '\n' +
        'All of the above AND' + ' ' +
        'bank statements, tax codes, reports, sale orders' + '\n\n' +

        'Manager' + '\n' +
        'All of the above AND' + ' ' +
        'tax templates, account charts, payment terms, taxes,' + ' ' +
        'journals, fiscal years, currencies, etc.'
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

        help='HR PERMISSIONS' + '\n\n' +
        'Employee' + '\n' +
        'Resources, leaves, messages, mails, documents,' + ' ' +
        'notifications, discussions, events, calendars,' + ' ' +
        'procurements, analytic journal' + '\n\n' +

        'Officer' + '\n' +
        'All of the above AND' + ' ' +
        'employees, resource details, jobs, attendance, timesheets' + '\n\n' +

        'Manager' + '\n' +
        'All of the above AND' + ' ' +
        'costs, taxes'
    )

    ''' STOCK / WAREHOUSE '''
    show_group_stock = fields.Boolean(
        compute='compute_show_group_stock',
    )
    group_stock = fields.Selection(
        selection='get_group_stock',
        inverse='set_group_stock',
        string='Warehouse',
        default='user',

        help='WAREHOUSE PERMISSIONS' + '\n\n' +
        'User' + '\n' +
        'Picking lists, moves, inventory, products, invoices' + '\n\n' +

        'Manager' + '\n' +
        'All of the above AND' + ' ' +
        'incoterms, warehouses, locations, product categories,' + " " +
        'packaging, pricelists, procurements, routes'
    )

    ''' MANUFACTURING '''
    show_group_mrp = fields.Boolean(
        compute='compute_show_group_mrp',
    )
    group_mrp = fields.Selection(
        selection='get_group_mrp',
        inverse='set_group_mrp',
        string='Manufacturing',
        default='user',

        help='MANUFACTURING PERMISSIONS' + '\n\n' +
        'User' + '\n' +
        'Work centers, routings, bill of materials, manufacturing,' + ' ' +
        'stock moves, picking lists, work orders' + '\n\n' +

        'Manager' + '\n' +
        'All of the above AND' + ' ' +
        'resource calendars, work center loads, stock value variation' + " " +
        'units of measure, packaging, pricelists, etc.'
    )

    ''' WEBSITE '''
    show_group_website = fields.Boolean(
        compute='compute_show_group_website',
    )
    group_website = fields.Selection(
        selection='get_group_website',
        inverse='set_group_website',
        string='Website',

        help='WEBSITE PERMISSIONS' + '\n\n' +
        'Display Editor Bar on Website' + '\n' +
        'Display Editor Bar on Website' + '\n\n' +

        'Manage Website' + '\n' +
        'Website, website menu, SEO metadata, qWeb view'
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
        group = False

        if self.group_sales == 'user':
            group = self.get_group_by_name("See all Leads", category_name)

        elif self.group_sales == 'manager':
            group = self.get_group_by_name("Manager", category_name)

        self.set_group(group, category_name)

    ''' PURCHASES '''
    def get_group_purchase(self):
        group = [
            ('user', 'User'),
            ('manager', 'Manager'),
        ]

        return group

    def set_group_purchase(self):
        category_name = "Purchases"
        group = False

        if self.group_purchase == 'user':
            group = self.get_group_by_name("User", category_name)

        elif self.group_purchase == 'manager':
            group = self.get_group_by_name("Manager", category_name)

        self.set_group(group, category_name)

    ''' PROJECT '''
    def get_group_project(self):
        group = [
            ('user', 'User'),
            ('manager', 'Manager'),
        ]

        return group

    def set_group_project(self):
        category_name = "Project"
        group = False

        if self.group_project == 'user':
            group = self.get_group_by_name("User", category_name)

        elif self.group_project == 'manager':
            group = self.get_group_by_name("Manager", category_name)

        self.set_group(group, category_name)

    ''' ACCOUNT '''
    def get_group_account(self):
        group = [
            ('invoicing', 'Invoicing'),
            ('accountant', 'Accountant'),
            ('manager', 'Manager'),
        ]

        return group

    def set_group_account(self):
        category_name = "Accounting"
        group = False

        if self.group_account == 'invoicing':
            group = self.get_group_by_name("Invoicing", category_name)

        elif self.group_account == 'accountant':
            group = self.get_group_by_name("Accountant", category_name)

        elif self.group_account == 'manager':
            group = self.get_group_by_name("Financial Manager", category_name)

        self.set_group(group, category_name)

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
        group = False

        if self.group_hr == 'employee':
            group = self.get_group_by_name("Employee", category_name)

        elif self.group_hr == 'officer':
            group = self.get_group_by_name("Officer", category_name)

        elif self.group_hr == 'manager':
            group = self.get_group_by_name("Manager", category_name)

        self.set_group(group, category_name)

    ''' WAREHOUSE / STOCK '''
    def get_group_stock(self):
        group = [
            ('user', 'User'),
            ('manager', 'Manager'),
        ]

        return group

    def set_group_stock(self):
        category_name = "Warehouse"
        group = False

        if self.group_stock == 'user':
            group = self.get_group_by_name("User", category_name)

        elif self.group_stock == 'manager':
            group = self.get_group_by_name("Manager", category_name)

        self.set_group(group, category_name)

    ''' MRP / MANUFACTURING '''
    def get_group_mrp(self):
        return self.get_group("Manufacturing")

    def set_group_mrp(self):
        category_name = "Manufacturing"
        new_group = False

        for group in self.get_group_mrp():
            if self.group_mrp == group[0]:
                new_group = self.get_group_by_name(group[1], category_name)

        self.set_group(new_group, category_name)

    ''' WEBSITE '''
    def get_group_website(self):
        return self.get_group("Website")

    def set_group_website(self):
        category_name = "Website"
        new_group = False

        for group in self.get_group_website():
            if self.group_website == group[0]:
                new_group = self.get_group_by_name(group[1], category_name)

        self.set_group(new_group, category_name)

    def get_group(self, category_name):
        groups = []

        for group in self.get_groups_by_category_name(category_name):
            groups.append((group.name.lower(), group.name))

        return groups

    def set_group(self, new_group, category_name):
        groups = self.get_groups_by_category_name(category_name)

        ''' Unset current groups '''
        for unset_group in groups:
            self.sudo().user_id.groups_id = [(3, unset_group.id)]

        ''' Set the new group '''
        if new_group:
            self.sudo().user_id.groups_id = [(4, new_group.id)]
