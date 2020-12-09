from odoo import api
from odoo import fields
from odoo import models


class User(models.Model):
    _inherit = "res.users"

    user_task_ids = fields.One2many(
        string="User tasks",
        comodel_name="project.task",
        inverse_name="user_id",
        domain=[("stage_id.fold", "!=", True)],
    )
    user_task_count = fields.Integer(
        string="User task count", compute="_compute_user_task_count"
    )

    def _compute_user_task_count(self):
        for record in self:
            record.user_task_count = len(record.user_task_ids)
