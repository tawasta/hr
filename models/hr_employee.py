# -*- coding: utf-8 -*-

# 1. Standard library imports:
#	import base64

# 2. Known third party imports (One per line sorted and splitted in python stdlib):
#	import lxml

# 3. Odoo imports (openerp):
from openerp import api, fields, models

# 4. Imports from Odoo modules (rarely, and only if necessary):
#	from openerp.addons.website.models.website import slug

# 5. Local imports in the relative form:
#	from . import utils

# 6. Unknown third party imports (One per line sorted and splitted in python stdlib):
#	_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    
    # 1. Private attributes
    _inherit = 'hr.employee'


    # 2. Fields declaration
    show_all = fields.Boolean(
        'Show all fields',
        help="Some of the lesser used fields are hidden by default"
    )


    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
    