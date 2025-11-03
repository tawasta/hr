from odoo import models, _
from odoo.exceptions import UserError

from odoo.addons.hr_expense.models.hr_expense_sheet import HrExpenseSheet
from odoo.addons.mail.models.mail_thread import MailThread


# Disables messages of hr_timesheet module
def _track_subtype(self, init_values):
    return MailThread._track_subtype(self, init_values)


HrExpenseSheet._track_subtype = _track_subtype


class HrExpenseSheet(models.Model):
    _name = "hr.expense.sheet"
    _inherit = ["hr.expense.sheet", "mail.thread"]

    def action_submit_sheet(self):
        res = super().action_submit_sheet()

        subtype_id = self.env["ir.model.data"]._xmlid_to_res_id("mail.mt_comment")

        for sheet in self:
            sheet.message_post_with_source(
                "hr_expense_sheet_status_message.hr_expense_template_message_submit",
                subtype_id=subtype_id,
                render_values={"name": sheet.name},
            )

        return res

    def action_approve_expense_sheets(self):
        res = super().action_approve_expense_sheets()

        subtype_id = self.env["ir.model.data"]._xmlid_to_res_id("mail.mt_comment")

        for sheet in self:
            sheet.message_post_with_source(
                "hr_expense_sheet_status_message.hr_expense_template_message_approve",
                subtype_id=subtype_id,
                render_values={"name": sheet.name},
            )

        return res

    def _do_refuse(self, reason):
        """Same function as in code, but here it just uses a different mail template"""
        if self.account_move_ids:
            raise UserError(
                _("You cannot cancel an expense sheet linked to a journal entry")
            )
        self.approval_state = "cancel"
        subtype_id = self.env["ir.model.data"]._xmlid_to_res_id("mail.mt_comment")
        for sheet in self:
            sheet.message_post_with_source(
                "hr_expense_sheet_status_message.hr_expense_template_message_refuse",
                subtype_id=subtype_id,
                render_values={"reason": reason, "name": sheet.name},
            )
        self.activity_update()
