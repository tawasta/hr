from odoo import _, models
from odoo.exceptions import UserError

from odoo.addons.hr_expense.models.hr_expense_sheet import HrExpenseSheet
from odoo.addons.mail.models.mail_thread import MailThread


# Disables messages of hr_expense module
def _track_subtype(self, init_values):
    return MailThread._track_subtype(self, init_values)


HrExpenseSheet._track_subtype = _track_subtype


class HrExpenseSheet(models.Model):
    _name = "hr.expense.sheet"
    _inherit = ["hr.expense.sheet", "mail.thread"]

    def action_submit_sheet(self):
        res = super().action_submit_sheet()

        for sheet in self:
            if sheet.user_id:
                optional_receiver = self.env["res.partner"].search(
                    [("submit_message_receiver", "=", True)]
                )
                send_partners = [sheet.user_id.partner_id.id]

                if optional_receiver:
                    send_partners.append(optional_receiver.id)

                sheet.message_post_with_source(
                    "hr_expense_sheet_status_message.hr_expense_template_message_submit_layout",
                    subtype_xmlid="mail.mt_note",
                    subject=_("Submitted expense report"),
                    render_values={
                        "name": sheet.name,
                        "partner": sheet.user_id.partner_id,
                        "record": sheet,
                    },
                    email_layout_xmlid="mail.mail_notification_light",
                    partner_ids=send_partners,
                    email_from=sheet.company_id.email,
                )

        return res

    def action_approve_expense_sheets(self):
        res = super().action_approve_expense_sheets()

        for sheet in self:
            sheet.message_post_with_source(
                "hr_expense_sheet_status_message.hr_expense_template_message_approve_layout",
                subtype_xmlid="mail.mt_note",
                subject=_("Approved expense report"),
                render_values={
                    "name": sheet.name,
                    "partner": sheet.user_id.partner_id,
                    "record": sheet,
                },
                email_layout_xmlid="mail.mail_notification_light",
                partner_ids=[sheet.employee_id.user_id.partner_id.id],
                email_from=sheet.company_id.email,
            )

        return res

    def _do_refuse(self, reason):
        """Same function as in code, but here it just uses a different mail template"""
        if self.account_move_ids:
            raise UserError(
                _("You cannot cancel an expense sheet linked to a journal entry")
            )
        self.approval_state = "cancel"
        for sheet in self:
            sheet.message_post_with_source(
                "hr_expense_sheet_status_message.hr_expense_template_message_refuse_layout",
                subtype_xmlid="mail.mt_note",
                subject=_("Refused expense report"),
                render_values={
                    "name": sheet.name,
                    "partner": sheet.user_id.partner_id,
                    "record": sheet,
                    "reason": reason,
                },
                email_layout_xmlid="mail.mail_notification_light",
                partner_ids=[sheet.employee_id.user_id.partner_id.id],
                email_from=sheet.company_id.email,
            )
        self.activity_update()
