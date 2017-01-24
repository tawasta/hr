# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from openerp import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class AccountAnalyticLine(models.Model):
    
    # 1. Private attributes
    _inherit = 'account.analytic.line'

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
    @api.model
    def _prepare_cost_invoice(self, partner, company_id, currency_id, analytic_lines):
        res = super(AccountAnalyticLine, self)._prepare_cost_invoice(
            partner=partner,
            company_id=company_id,
            currency_id=currency_id,
            analytic_lines=analytic_lines,
        )

        if analytic_lines[0].account_id.invoice_reference:
            res['name'] = analytic_lines[0].account_id.invoice_reference

        return res

    @api.model
    def _prepare_cost_invoice_line(
            self, invoice_id, product_id, uom, user_id, factor_id, account, analytic_lines, journal_type, data):

        res = super(AccountAnalyticLine, self)._prepare_cost_invoice_line(
            invoice_id=invoice_id,
            product_id=product_id,
            uom=uom,
            user_id=user_id,
            factor_id=factor_id,
            account=account,
            analytic_lines=analytic_lines,
            journal_type=journal_type,
            data=data,
        )

        line_name = ""

        products = list()
        for analytic_line in analytic_lines:
            products.append(analytic_line.task_id.name)

        products = set(products)

        pos = 0
        for product in products:
            pos += 1

            line_name += product

            if not pos == len(products):
                line_name += "\n"

        res['name'] = line_name

        return res
