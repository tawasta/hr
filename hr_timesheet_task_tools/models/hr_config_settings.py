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
        task_works = self.env['project.task.work'].search(
            []
        )
        # analytic_lines = self.env['hr.analytic.timesheet'].search(
        #     []
        # )
        for work in task_works:

            if work.hr_analytic_timesheet_id:
                if not work.hr_analytic_timesheet_id.line_id.task_id:
                    self._cr.execute(
                        "UPDATE account_analytic_line SET task_id = %s WHERE id = %s",
                        (work.task_id.id, work.hr_analytic_timesheet_id.line_id.id)
                    )
                    count += 1
            else:
                notFound += 1
            #     for analytic_line in analytic_lines:
            #         task_name = analytic_line.line_id.name.split(':')

            #         if len(task_name) :

            # _logger.warning("Multiple tasks found! (%s)" % task_id.ids)
        _logger.info("Found %s task works!" % len(task_works))
        _logger.info("Inserted to %s timesheets!" % count)
        _logger.warning("Timesheets null on task_works: %s" % notFound)

        # count = 0

        # analytic_lines = self.env['hr.analytic.timesheet'].search(
        #     []
        # )
        # _logger.info("Found %s timesheet lines" % len(analytic_lines))

        # for analytic_line in analytic_lines:
        # task_name = analytic_line.line_id.name.split(':')

        # if len(task_name) < 1:
        #     continue

        # task_id = self.env['project.task'].search([
        #     ('name', '=', task_name[0]),
        #     ('project_id.name', '=', analytic_line.account_id.name)
        # ])

        # # No task found
        # if not task_id:
        #     continue

        # if len(task_id) == 1:
        #     self._cr.execute(
        #         "UPDATE account_analytic_line SET task_id = %s WHERE id = %s",
        #         (task_id.id, analytic_line.line_id.id)
        #     )

        #     count += 1
        # else:
        # Right task for the line
        # if not analytic_line.task_id:

        # task_work = self.env['project.task.work'].search([
        #     ('hr_analytic_timesheet_id','=', analytic_line.id)
        # ])
        # if task_work:
        # self._cr.execute(
        #     "UPDATE account_analytic_line SET task_id = %s WHERE id = %s",
        #     (task_work.task_id.id, analytic_line.line_id.id)
        # )
        # # _logger.warning("Multiple tasks found! (%s)" % task_id.ids)
        # _logger.warning("Right task found! (%s)" % task_work.task_id)
        # count += 1

        # count += 1

        # _logger.info("Updated %s timesheet lines" % count)
