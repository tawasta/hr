# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrApplicant(models.Model):

    _inherit = 'hr.applicant'

    employee_categ_ids = fields.Many2many(related='emp_id.category_ids', relation='hr.employee.category', string='Tags', readonly=True)