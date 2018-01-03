# -*- coding: utf-8 -*-
from datetime import datetime
from openerp import api, models, _


class HrTimesheetSheet(models.Model):
    
    _inherit = 'hr_timesheet_sheet.sheet'

    # Overwrite the name get
    @api.multi
    def name_get(self):
        # week number according to ISO 8601 Calendar
        return [(r['id'], _('Week ') + str(
            datetime.strptime(r['date_from'], '%Y-%m-%d').isocalendar()[1]))
                for r in self.read(['date_from'], load='_classic_write')]
