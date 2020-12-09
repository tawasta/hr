from odoo import fields
from odoo import models


class AccountAnalyticLine(models.Model):

    _inherit = "account.analytic.line"

    task_type_id = fields.Many2one(
        comodel_name="project.type",
        related="task_id.type_id",
        store=True,
        string="Task type",
    )
