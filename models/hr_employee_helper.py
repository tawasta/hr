# -*- coding: utf-8 -*-
from openerp import models, api
from openerp import _


class HrEmployeeHelper(models.Model):
    _inherit = 'hr.employee'

    def get_group_by_name(self, group_name, category_name):
        # Gets security group by group name
        groups_obj = self.env['res.groups']

        groups = self.get_groups_by_category_name(category_name)

        # Search without lang
        group = groups_obj.sudo().with_context(lang=False).\
            search([('name', 'ilike', group_name),
                    ('id', 'in', groups.ids)])

        return group

    def get_groups_by_category_name(self, category_name):
        # Gets security groups by category name
        groups_obj = self.env['res.groups']

        # Search without lang
        groups = groups_obj.sudo().with_context(lang=False).search(
            [('category_id.name', 'ilike', category_name)]
        )

        return groups

    def get_default_groups(self):
        groups = []

        groups.append(
            self.get_group_by_name('See all Leads', 'Sales').id or False)
        groups.append(
            self.get_group_by_name('Employee', 'Human Resources').id or False)

        groups = filter(None, groups)

        return tuple(groups)

    @api.one
    def action_reset_password(self):
        res = self.sudo().user_id.action_reset_password()

        url = self.sudo().user_id.signup_url

        msg = _("An invitation mail to")
        msg += " <b>%s</b> " % self.user_id.partner_id.email
        msg += _("containing subcription link")
        msg += " <a href='%s'><b>%s</b></a> " % (url, url)
        msg += _("has been sent")

        self.message_post(msg)

        return res

    def compute_show_group(self, module_name):
        visible = False

        if self.get_module_status(module_name):
            visible = True

        return visible

    ''' Field visibility helpers '''
    ''' TODO: could this be done in one method? '''
    def compute_show_group_sales(self):
        self.show_group_sales = self.compute_show_group('sale')

    def compute_show_group_purchase(self):
        self.show_group_purchase = self.compute_show_group('purchase')

    def compute_show_group_project(self):
        self.show_group_project = self.compute_show_group('project')

    def compute_show_group_account(self):
        self.show_group_account = self.compute_show_group('account')

    def compute_show_group_hr(self):
        self.show_group_hr = self.compute_show_group('hr')

    def compute_show_group_stock(self):
        self.show_group_stock = self.compute_show_group('stock')

    def compute_show_group_mrp(self):
        self.show_group_mrp = self.compute_show_group('mrp')

    def compute_show_group_website(self):
        self.show_group_website = self.compute_show_group('website')

    def get_module_status(self, module_name):
        ''' If the module is installed, returns true '''
        modules = self.env['ir.module.module']

        installed = False

        if modules.search([
            ('name', '=', module_name),
            ('state', '=', 'installed')
        ]):
            installed = True

        return installed
