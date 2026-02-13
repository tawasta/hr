from odoo import _, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def action_decrypt_employee_social_security_number(self):
        self.ensure_one()
        if not self.work_contact_id:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("No Private Contact"),
                    "message": _("This employee has no private contact (work contact)."),
                    "sticky": False,
                },
            }

        return {
            "name": _("Decrypt Personal ID"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "hr.employee.ssn.decrypt.wizard",
            "target": "new",
            "context": {"default_employee_id": self.id},
        }
