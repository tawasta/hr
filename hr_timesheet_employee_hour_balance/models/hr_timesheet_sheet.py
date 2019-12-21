from odoo import  models, fields


class HrTimesheetSheet(models.Model):

    _inherit = 'hr_timesheet_sheet.sheet'

    calendar_id = fields.Many2one(
        comodel_name='resource.calendar',
        related='employee_id.calendar_id',
        readonly=True,
    )

    total_hours = fields.Float(
        related='employee_id.calendar_id.total_hours',
        readonly=True,
    )

    total_remaining = fields.Float(
        string='Total remaining',
        compute='_compute_total_remaining',
    )

    def _compute_total_remaining(self):
        for record in self:
            if record.total_timesheet and record.total_hours:
                record.total_remaining = \
                    record.total_timesheet - record.total_hours