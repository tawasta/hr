from odoo import models, fields, api


class ResourceCalendar(models.Model):

    _inherit = 'resource.calendar'

    total_hours = fields.Float(
        string="Total hours",
        help="Working time within the timespan",
        compute='_compute_total_hours',
        store=True,
    )

    @api.depends('attendance_ids.hour_from', 'attendance_ids.hour_to')
    def _compute_total_hours(self):
        for record in self:
            record.total_hours = sum(
                attendance.total_hours for attendance in
                record.attendance_ids
            )
