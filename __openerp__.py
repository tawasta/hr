# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2015- Oy Tawasta Technologies Ltd. (http://www.tawasta.fi)
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
    'name': 'HR User',
    'category': 'CRM',
    'version': '8.0.0.1.0',
    'author': 'Oy Tawasta Technologies Ltd.',
    'website': 'http://www.tawasta.fi',
    'depends': [
        'hr',
        'auth_signup',
    ],
    'description': '''
HR User
-------

Allows adding users from HR-module.

Features
========
* Allows creating user from employee form
* Allows editing sales role from employee form
* Allows editing HR role from employee form
* Allow sending invitaiton link from employee form
''',
    'data': [
        'view/hr_employee_form.xml',
    ],
}
