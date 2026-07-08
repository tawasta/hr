from odoo import _, api, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    @api.model_create_multi
    def create(self, vals_list):
        expenses = super().create(vals_list)

        if self.env.context.get("website_id"):
            default_job_id_str = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("hr_autofill_employee_job_title.default_job_id", "")
            )

            if default_job_id_str:
                try:
                    default_job = (
                        self.env["hr.job"]
                        .sudo()
                        .browse(int(default_job_id_str))
                        .exists()
                    )
                except (ValueError, TypeError):
                    default_job = self.env["hr.job"]

                if default_job:
                    employees_to_update = self.env["hr.employee"]
                    for expense in expenses:
                        if expense.employee_id and not expense.employee_id.job_id:
                            employees_to_update |= expense.employee_id
                    if employees_to_update:
                        employees_to_update.write(
                            {
                                "job_id": default_job.id,
                                "job_title": default_job.name,
                            }
                        )
                        employees_to_update.message_post(
                            body=_(
                                "This user was automatically assigned to job position "
                                "%s as a result of submitting an expense report.",
                                default_job.name,
                            )
                        )
        return expenses
