from odoo import _, api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def action_decrypt_employee_social_security_number(self):
        self.ensure_one()
        if not self.work_contact_id:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("No Private Contact"),
                    "message": _(
                        "This employee has no private contact (work contact)."
                    ),
                    "sticky": False,
                },
            }

        return {
            "name": _("Decrypt Personal ID"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "hr.employee.ssn.decrypt.wizard",
            "target": "new",
            "context": {"default_employee_id": self.id},
        }


class HrExpense(models.Model):
    _inherit = "hr.expense"

    portal_manual_price = fields.Boolean(default=False)

    @api.depends("product_id.standard_price")
    def _compute_from_product(self):
        for expense in self:
            expense.product_has_cost = (
                expense.product_id
                and not expense.company_currency_id.is_zero(
                    expense.product_id.standard_price
                )
            )

            tax_ids = expense.product_id.supplier_taxes_id.filtered_domain(
                self.env["account.tax"]._check_company_domain(expense.company_id)
            )
            expense.product_has_tax = bool(tax_ids)

            # Core Odoo resetoi qty=1 jos product_has_cost=False.
            # Portaali-expenseillä tätä EI tehdä.
            if (
                not expense.portal_manual_price
                and not expense.product_has_cost
                and expense.state in {"draft", "reported"}
                and expense.quantity != 1
            ):
                expense.quantity = 1

    def _needs_product_price_computation(self):
        self.ensure_one()
        if self.portal_manual_price:
            return False
        return super()._needs_product_price_computation()

    @api.onchange("quantity", "price_unit")
    def _onchange_portal_manual_price_amounts(self):
        for expense in self:
            if not expense.portal_manual_price:
                continue

            expense.total_amount_currency = expense.quantity * expense.price_unit
            expense.total_amount = expense.total_amount_currency

    def write(self, vals):
        if "quantity" in vals or "price_unit" in vals:
            vals = dict(vals)

            for expense in self:
                if not expense.portal_manual_price:
                    continue

                qty = vals.get("quantity", expense.quantity)
                unit = vals.get("price_unit", expense.price_unit)
                vals["total_amount_currency"] = qty * unit

        return super().write(vals)
