from odoo import fields, models


class EmployeeSkill(models.Model):
    _inherit = "hr.employee.skill"

    # Direct, stored related so we can safely group/order by department
    department_id = fields.Many2one(
        "hr.department",
        related="employee_id.department_id",
        store=True,
        index=True,
        readonly=True,
    )

class HrSkillType(models.Model):
    _inherit = "hr.skill.type"

    sequence = fields.Integer(default=10)
