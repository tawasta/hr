from odoo import models


class HrExpenseSheet(models.Model):
    _name = "hr.expense.sheet"
    _inherit = ["hr.expense.sheet", "mail.thread"]

    def action_submit_sheet(self):
        res = super().action_submit_sheet()

        subtype_id = self.env["ir.model.data"]._xmlid_to_res_id("mail.mt_comment")

        for sheet in self:
            sheet.sudo().message_post_with_source(
                "hr_expense_sheet_status_message.hr_expense_template_submit_message",
                subtype_id=subtype_id,
                render_values={"name": sheet.name},
            )

        return res

    def action_approve_expense_sheets(self):
        res = super().action_approve_expense_sheets()

        subtype_id = self.env["ir.model.data"]._xmlid_to_res_id("mail.mt_comment")

        for sheet in self:
            sheet.sudo().message_post_with_source(
                "hr_expense_sheet_status_message.hr_expense_template_approve_message",
                subtype_id=subtype_id,
                render_values={"name": sheet.name},
            )

        return res
