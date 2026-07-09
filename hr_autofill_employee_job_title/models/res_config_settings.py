from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    hr_employee_default_job_id = fields.Many2one(
        "hr.job",
        string="Default Employee Job Position",
        help=(
            "Default job position assigned to employees "
            "created from an expense report."
        ),
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        IrConfigParameter = self.env["ir.config_parameter"].sudo()

        default_job_id = IrConfigParameter.get_param(
            "hr_autofill_employee_job_title.default_job_id"
        )
        if default_job_id:
            res.update(hr_employee_default_job_id=int(default_job_id))
        else:
            old_title = IrConfigParameter.get_param(
                "hr_autofill_employee_job_title.default_job_title", ""
            )
            if old_title:
                job = (
                    self.env["hr.job"]
                    .sudo()
                    .search([("name", "=ilike", old_title)], limit=1)
                )
                if job:
                    res.update(hr_employee_default_job_id=job.id)
        return res

    def set_values(self):
        res = super().set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "hr_autofill_employee_job_title.default_job_id",
            self.hr_employee_default_job_id.id or False,
        )
        return res
