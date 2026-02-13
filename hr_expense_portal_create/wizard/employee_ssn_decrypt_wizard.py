from odoo import _, fields, models


class HrEmployeeSSNDecryptWizard(models.TransientModel):
    _name = "hr.employee.ssn.decrypt.wizard"
    _description = "Decrypt Employee Personal ID"

    key = fields.Char(string="Decryption Key", required=True, password=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)

    def decrypt_social_security_number(self):
        self.ensure_one()
        employee = self.employee_id
        partner = employee.work_contact_id

        if not partner or not partner.encrypted_social_security_number:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("No Personal Identification Number"),
                    "message": _(
                        "No encrypted personal identification number found on the employee's private contact."  # noqa: E501
                    ),
                    "sticky": False,
                },
            }

        decrypted = partner.decrypt_social_security_number(
            partner.encrypted_social_security_number,
            self.key,
        )

        if decrypted in (
            _("The key you provided is incorrect."),
            _("Decryption failed"),
        ):
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Decryption failed"),
                    "message": decrypted,
                    "sticky": False,
                },
            }

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Decrypted Personal Identification Number"),
                "message": decrypted,
                "sticky": False,
            },
        }
