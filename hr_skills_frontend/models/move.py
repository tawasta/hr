from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    def _skills_access_total_days_from_invoice_lines(self):
        self.ensure_one()
        total_days = 0
        for line in self.invoice_line_ids:
            product = line.product_id
            if not product:
                continue
            if not (product.skills_portal_grant and product.skills_portal_days > 0):
                continue
            qty = line.quantity or 1.0
            total_days += int(product.skills_portal_days * qty)
        return total_days

    def _grant_skills_access_if_needed(self):
        Access = self.env["hr.skills.portal.access"].sudo()
        now = fields.Datetime.now()

        for move in self:
            if move.payment_state != "paid":
                continue

            if Access.search_count([("invoice_id", "=", move.id)]):
                continue

            total_days = move._skills_access_total_days_from_invoice_lines()
            if total_days <= 0:
                continue

            partner = move.partner_id
            user = partner._get_or_create_portal_user() if partner else False
            if not user:
                continue

            # Etsi uusin grant (aktiivinen TAI tuleva), jotta uusi alkaa siitä mihin edellinen päättyy
            last_grant = Access.search(
                [
                    ("user_id", "=", user.id),
                    ("active", "=", True),
                    ("date_end", ">=", now),  # huom: tulevatkin mukana jos date_end tulevaisuudessa
                ],
                order="date_end desc",
                limit=1,
            )

            if last_grant:
                # Uusi alkaa tasan edellisen lopusta (jatkuu siitä)
                start = last_grant.date_end
            else:
                # Ei aiempaa voimassa olevaa/tulevaa -> alkaa nyt
                start = now

            end = fields.Datetime.add(start, days=total_days)

            Access.create({
                "user_id": user.id,
                "date_start": start,
                "date_end": end,
                "active": True,
                "invoice_id": move.id,
                "notes": f"Auto-granted from paid invoice/receipt {move.name}. Duration: {total_days} days.",
            })


    def _track_subtype(self, init_values):
        self.ensure_one()
        subtype = super()._track_subtype(init_values)

        if (
            self.is_invoice(include_receipts=True)
            and "payment_state" in init_values
            and self.payment_state == "paid"
        ):
            self._grant_skills_access_if_needed()

        return subtype
