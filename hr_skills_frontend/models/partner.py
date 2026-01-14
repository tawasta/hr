from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_or_create_portal_user(self):
        """Return a res.users for this partner; create a portal user if none exists."""
        self.ensure_one()
        Users = self.env["res.users"].sudo()

        user = Users.search([("partner_id", "=", self.id)], limit=1)
        if user:
            return user

        if not self.email:
            return False

        portal_group = self.env.ref("base.group_portal")
        return Users.create({
            "name": self.name or self.email,
            "login": self.email,
            "email": self.email,
            "partner_id": self.id,
            "groups_id": [(6, 0, [portal_group.id])],
        })
