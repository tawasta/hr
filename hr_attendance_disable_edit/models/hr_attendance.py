from odoo import api
from odoo import models
from odoo import _
from odoo.exceptions import UserError


class HrAttendance(models.Model):

    _inherit = "hr.attendance"

    @api.multi
    def write(self, vals):
        for record in self:
            if record.check_out and not self.env.user.has_group(
                "hr_attendance.group_hr_attendance_user"
            ):
                raise UserError(_("Can not edit an attendance after signing out"))

        return super().write(vals)
