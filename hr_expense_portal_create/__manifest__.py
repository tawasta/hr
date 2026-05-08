##############################################################################
#
#    Author: Futural Oy
#    Copyright 2019 Futural Oy (https://futural.fi)
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
    "name": "HR Expense Portal - Create Expenses",
    "summary": "HR Expense Portal - Create Expenses",
    "version": "17.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/tawasta/hr",
    "author": "Futural",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "portal",
        "hr_expense",
        "hr_expense_portal",
        "social_security_number_management",
        "privacy_profile",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/portal_templates.xml",
        "views/employee.xml",
        "views/product.xml",
        "views/hr_expense_views.xml",
        "wizard/employee_ssn_decrypt_wizard.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            # Same CDN stack as your other module
            "https://cdn.jsdelivr.net/npm/@eonasdan/tempus-dominus@6.9.4/dist/css/tempus-dominus.min.css",
            "https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.6/dist/umd/popper.min.js",
            "https://cdn.jsdelivr.net/npm/@eonasdan/tempus-dominus@6.9.4/dist/js/tempus-dominus.min.js",
            # Our init
            "/hr_expense_portal_create/static/src/js/portal_expense_create.esm.js",
        ],
    },
}
