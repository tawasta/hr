from odoo import api
from odoo import fields
from odoo import models


class ProjectTask(models.Model):
    _inherit = "project.task"

    employee_id = fields.Many2one(
        string="Employee",
        comodel_name="hr.employee",
        domain=[("user_id", "!=", False)],
        compute="_compute_employee_id",
        store=True,
        readonly=False,
    )

    @api.model
    def create(self, values):
        if "user_id" in values:
            # Force using the correct employee
            values["employee_id"] = self._get_employee_id(values.get("user_id"))

        return super(ProjectTask, self).create(values)

    @api.multi
    def write(self, values):
        if "user_id" in values:
            # Force using the correct employee
            values["employee_id"] = self._get_employee_id(values.get("user_id"))

        return super(ProjectTask, self).write(values)

    def _get_employee_id(self, user_id):
        if not user_id:
            employee = False
        else:
            employee = self.env["hr.employee"].search([("user_id", "=", user_id)]).id

        return employee

    def _compute_employee_id(self):
        for record in self:
            record.employee_id = self.env["hr.employee"].search(
                [("user_id", "=", record.user_id.id)], limit=1
            )

    @api.onchange("employee_id")
    @api.depends("employee_id")
    def onchange_employee_id_update_user(self):
        for record in self:
            if record.employee_id.user_id:
                record.user_id = record.employee_id.user_id
