from odoo import fields
from odoo import models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    user_task_ids = fields.One2many(related="user_id.user_task_ids")
    user_task_count = fields.Integer(related="user_id.user_task_count")

    def action_show_tasks(self):
        self.ensure_one()
        action = self.env.ref("project.action_view_task").read()[0]
        action["domain"] = [("user_id", "=", self.user_id.id)]

        return action
