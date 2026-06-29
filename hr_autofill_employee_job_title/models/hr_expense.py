import logging

from odoo import _, api, models

_logger = logging.getLogger(__name__)


class HrExpense(models.Model):
    _inherit = "hr.expense"

    @api.model_create_multi
    def create(self, vals_list):
        expenses = super().create(vals_list)

        if self.env.context.get("website_id"):
            default_title = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("hr_autofill_employee_job_title.default_job_title", "")
            )
            if default_title:
                employees_to_update = self.env["hr.employee"]
                for expense in expenses:
                    if expense.employee_id and not expense.employee_id.job_title:
                        employees_to_update |= expense.employee_id
                if employees_to_update:
                    employees_to_update.write({"job_title": default_title})
                    employees_to_update.message_post(
                        body=_(
                            "This user was automatically given a job title "
                            "%s as a result of submitting an expense report.",
                            default_title,
                        )
                    )
        else:
            _logger.info("HR_AUTOFILL EXPENSE: no website_id in context")

        return expenses
