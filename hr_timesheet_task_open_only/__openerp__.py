# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2016 Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################

{
    'name': 'Timesheet only show open tasks',
    'summary': 'Only show open tasks on timesheets',
    'version': '8.0.1.1.3',
    'category': 'HR',
    'website': 'http://www.tawasta.fi',
    'author': 'Oy Tawasta Technologies Ltd.',
    'license': 'AGPL-3',
    'application': False,
    'installable': False,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'project_stage_closed',
        'timesheet_task',
        'hr_timesheet_task',
    ],
    'data': [
        'views/hr_analytic_timesheet_tree.xml',
        'views/hr_timesheet_sheet_form.xml',
        'views/hr_timesheet_task_js.xml',
    ],
    'demo': [
    ],
}
