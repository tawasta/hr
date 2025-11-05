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
    "name": "HR Skills Frontend",
    "summary": "HR Skills Frontend",
    "version": "17.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/tawasta/hr",
    "author": "Futural",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "hr_skills",
        "website",
    ],
    "data": [
        "data/website_menu.xml",
        "data/ir_cron.xml",
        "security/ir.model.access.csv",
        "views/skills_portal_access_views.xml",
        "views/skills_portal.xml",
        "views/skills_profile_modal.xml",
        "wizard/skills_portal_quick_grant_wizard_views.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "/hr_skills_frontend/static/src/js/main.esm.js",
        ],
    },
}
