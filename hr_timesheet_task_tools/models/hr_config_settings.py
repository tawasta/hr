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

        analytic_lines = self.env['hr.analytic.timesheet'].search(
            []
        )
        _logger.info("Found %s timesheet lines" % len(analytic_lines))

        for analytic_line in analytic_lines:
            task_name = analytic_line.line_id.name.split(':')

            if len(task_name) < 1:
                continue

            task_id = self.env['project.task'].search([
                ('name', '=', task_name[0]),
                ('project_id.name', '=', analytic_line.account_id.name)
            ])

            # No task found
            if not task_id:
                continue

            if len(task_id) == 1:
                self._cr.execute(
                    "UPDATE account_analytic_line SET task_id = %s WHERE id = %s",
                    (task_id.id, analytic_line.line_id.id)
                )

                count += 1
            else:
                _logger.warning("Multiple tasks found! (%s)" % task_id.ids)


        _logger.info("Updated %s timesheet lines" % count)