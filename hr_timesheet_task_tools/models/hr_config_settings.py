# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from openerp import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:
import logging
_logger = logging.getLogger(__name__)


class HrConfigSettings(models.TransientModel):

    # 1. Private attributes
    _inherit = 'hr.config.settings'

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
    @api.multi
    def update_tasks_from_description(self):
        count = 0
        notFound = 0
        hardWay = 0
        task_works = self.env['project.task.work'].search(
            []
        )
        analytic_lines = self.env['hr.analytic.timesheet'].search(
            []
        )
        for work in task_works:

            if work.hr_analytic_timesheet_id:
                if not work.hr_analytic_timesheet_id.line_id.task_id:
                    task_id = work.task_id.id
                    line_id = work.hr_analytic_timesheet_id.line_id.id

                    _logger.debug("Updating task %s to timesheet %s" % (task_id, line_id))

                    self._cr.execute(
                        "UPDATE account_analytic_line SET task_id = %s WHERE id = %s",
                        (task_id, line_id)
                    )
                    count += 1
            else:
                notFound += 1
                for analytic_line in analytic_lines:
                    line_name = analytic_line.line_id.name.split(': ')

                    if len(line_name) == 1:
                        work_name=line_name[0]
                    
                    elif len(line_name) == 2:
                        work_name = line_name[1]
                    
                    else:
                        continue
                    
                    # If work name matches without split or with split
                    if  analytic_line.line_id.name == work.name or work_name == work.name:

                        self._cr.execute(
                            "UPDATE account_analytic_line SET task_id = %s WHERE id = %s",
                            (work.task_id.id, analytic_line.line_id.id)
                        )
                        _logger.warning("Timesheet: %s and Task: %s" % (analytic_line.line_id, work.task_id))

                        hardWay += 1

        
        _logger.info("Found %s task works!" % len(task_works))
        _logger.info("Inserted to %s timesheets!" % count)
        _logger.warning("Timesheets null on task_works: %s" % notFound)
        _logger.warning("Timesheets null on task_works and fixed: %s" % hardWay)
