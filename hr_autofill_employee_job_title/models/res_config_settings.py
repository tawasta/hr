from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    hr_employee_default_job_title = fields.Char(
        string="Default Employee Job Title",
        config_parameter="hr_autofill_employee_job_title.default_job_title",
        help="Default job title assigned to employees created from an expense report.",
    )
