# -*- coding: utf-8 -*-
from odoo import api, models


class HrTimesheetSheet(models.Model):

    _inherit = 'hr_timesheet_sheet.sheet'

    @api.model
    def create(self, values):
        domain = [
            ('company_id', '=', values.get('company_id')),
            ('employee_id', '=', values.get('employee_id')),
        ]
        previous_timesheet = self.search(domain, limit=1)

        res = super(HrTimesheetSheet, self).create(values)

        if previous_timesheet and not res.timesheet_ids:
            aal = self.env['account.analytic.line']
            tasks = []
            # Create empty lines for the new timesheet
            for line in previous_timesheet.timesheet_ids:

                if line.task_id in tasks:
                    # Only create one empty line for each task
                    continue
                tasks.append(line.task_id)

                new_line = {
                    'date': res.date_from,
                    'user_id': res.user_id.id,
                    'name': '/',
                    'project_id': line.project_id.id,
                    'task_id': line.task_id.id,
                }

                aal.create(new_line)

        return res
