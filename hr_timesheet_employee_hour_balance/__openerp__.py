# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2017- Vizucom Oy (http://www.vizucom.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Employee Hour Balance',
    'category': 'HR',
    'version': '8.0.1.0.0',
    'author': 'Vizucom Oy',
    'website': 'http://www.vizucom.com',
    'depends': ['hr_timesheet_sheet'],
    'description': """
Employee Hour Balance
=====================
 * Shows the hour balance for each employee from a certain date onwards, based on their weekly working hours
 * Adds two new groups, one for seeing own balance, and another for seeing all employees' balances
    """,
    'data': [
        'views/hr_employee.xml',
        'views/hr_employee_inherit.xml',
    ],
}
