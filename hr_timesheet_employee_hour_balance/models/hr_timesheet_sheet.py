from odoo import  models, fields


class HrTimesheetSheet(models.Model):

    _inherit = 'hr_timesheet.sheet'

    calendar_id = fields.Many2one(
        comodel_name='resource.calendar',
        related='employee_id.resource_calendar_id',
        readonly=True,
    )

    total_hours = fields.Float(
        related='calendar_id.total_hours',
        readonly=True,
    )

    total_remaining = fields.Float(
        string='Total remaining',
        compute='_compute_total_remaining',
    )

    def _compute_total_remaining(self):
        for record in self:
            if record.total_time and record.total_hours:
                record.total_remaining = \
                    record.total_time - record.total_hours
