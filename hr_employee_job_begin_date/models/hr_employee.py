from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    job_begin_date = fields.Date(
        string="Job begin date",
        default=fields.Date.context_today,
    )
