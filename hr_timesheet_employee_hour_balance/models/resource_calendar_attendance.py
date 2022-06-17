from odoo import api, fields, models


class ResourceCalendarAttendance(models.Model):

    _inherit = "resource.calendar.attendance"

    total_hours = fields.Float(help="Total hours within the day", readonly=True)

    @api.onchange("hour_from", "hour_to")
    def _compute_total_hours(self):
        for record in self:
            if record.hour_from and record.hour_to:
                record.total_hours = record.hour_to - record.hour_from
