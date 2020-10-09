# -*- coding: utf-8 -*-
from odoo import api, models


class HrTimesheetSheet(models.Model):

    _inherit = 'hr_timesheet_sheet.sheet'


    def action_autofill_tasks(self):
        for record in self:
            timesheet_domain = [
                ('company_id', '=', record.company_id.id),
                ('employee_id', '=', record.employee_id.id),
                ('id', '!=', record.id)
            ]
            previous_timesheet = self.search(timesheet_domain, limit=1)
            aal = self.env['account.analytic.line']

            if previous_timesheet:
                # Copy tasks from previous timesheets
                for line in previous_timesheet.timesheet_ids:
                    if line.task_id in record.timesheet_ids.mapped('task_id'):
                        # Don't create existing tasks
                        continue

                    # Create empty lines for the new timesheet
                    new_line = {
                        'date': record.date_from,
                        'user_id': record.user_id.id,
                        'name': '/',
                        'project_id': line.project_id.id,
                        'task_id': line.task_id.id,
                    }

                    aal.create(new_line)

