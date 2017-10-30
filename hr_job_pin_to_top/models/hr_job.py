# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrJob(models.Model):

    _inherit = 'hr.job'
    _order = 'pin_to_top DESC, id ASC'

    pin_to_top = fields.Boolean('Pin to top', default=False, help='''Pinned job positions are shown at the top of job listings''')