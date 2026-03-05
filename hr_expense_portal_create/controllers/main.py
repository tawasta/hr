import base64
import logging
from datetime import date, datetime

from odoo import _, http
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.hr_expense_portal.controllers.main import HrExpenseCustomerPortal

_logger = logging.getLogger(__name__)


class HrExpenseCustomerPortalCreate(HrExpenseCustomerPortal):
    def _portal_employee(self):
        employee = request.env.user.sudo().employee_id
        if not employee:
            raise ValidationError(
                _("The current user has no related employee. Please contact support.")
            )
        return employee

    def _allowed_products(self, company):
        Product = request.env["product.product"].sudo()
        domain = [
            ("can_be_expensed", "=", True),
            "|",
            ("company_id", "=", False),
            ("company_id", "=", company.id),
        ]
        return Product.search(domain, order="name asc")

    def _to_float(self, value, default=0.0):
        if value in (None, "", False):
            return default
        if isinstance(value, str):
            value = value.replace(" ", "").replace(",", ".")
        return float(value)

    def _to_int(self, value, default=0):
        try:
            if value in (None, "", False):
                return default
            return int(value)
        except Exception:
            return default

    def _normalize_date(self, raw_date):
        raw_date = (raw_date or "").strip()
        if not raw_date:
            return date.today().isoformat()

        for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
            try:
                return datetime.strptime(raw_date, fmt).date().isoformat()
            except ValueError as e:
                _logger.debug(
                    "Date parse failed for %r with format %s: %s", raw_date, fmt, e
                )

        _logger.warning("Invalid date input %r, falling back to today.", raw_date)
        return date.today().isoformat()

    def _create_attachments(self, uploads):
        Attachment = request.env["ir.attachment"].sudo()
        if not uploads:
            return Attachment

        created = Attachment
        for upload in uploads:
            if not upload or not getattr(upload, "filename", False):
                continue
            content = upload.read()
            if not content:
                continue

            created |= Attachment.create(
                {
                    "name": upload.filename,
                    "datas": base64.b64encode(content),
                    "mimetype": getattr(upload, "content_type", False)
                    or "application/octet-stream",
                    "res_model": "hr.expense",
                    "res_id": 0,
                }
            )
        return created

    def _create_privacy_consents(self, post, partner):
        PrivacyActivity = request.env["privacy.activity"].sudo()
        PrivacyConsent = request.env["privacy.consent"].sudo()

        activities = PrivacyActivity.search([("show_in_profile", "=", True)])
        if not activities:
            return True  # nothing to require/save

        accepted_ids = []
        for act in activities:
            if post.get("privacy_%s" % act.id):
                accepted_ids.append(act.id)

        # Require: all shown activities must be
        # accepted (matches required checkboxes in UI)
        if set(accepted_ids) != set(activities.ids):
            return False

        for act in activities:
            accepted = act.id in accepted_ids
            existing = PrivacyConsent.search(
                [("partner_id", "=", partner.id), ("activity_id", "=", act.id)],
                limit=1,
            )
            if existing:
                existing.write({"accepted": accepted, "state": "answered"})
            else:
                PrivacyConsent.create(
                    {
                        "partner_id": partner.id,
                        "activity_id": act.id,
                        "accepted": accepted,
                        "state": "answered",
                    }
                )
        return True

    def portal_my_expenses(
        self,
        page=1,
        sortby="date",
        filterby="all",
        search=None,
        search_in="all",
        groupby="none",
        **kw,
    ):
        response = super().portal_my_expenses(
            page=page,
            sortby=sortby,
            filterby=filterby,
            search=search,
            search_in=search_in,
            groupby=groupby,
            **kw,
        )
        try:
            company = request.env.company
            response.qcontext["today_fi"] = date.today().strftime("%d.%m.%Y")
            response.qcontext["products"] = self._allowed_products(company)

            employee = self._portal_employee()
            partner = employee.sudo().work_contact_id
            bank = employee.sudo().bank_account_id

            Country = request.env["res.country"].sudo()
            State = request.env["res.country.state"].sudo()

            response.qcontext.update(
                {
                    "employee": employee,
                    "partner": partner,
                    "partner_iban": bank.acc_number if bank else "",
                    "countries": Country.search([], order="name asc"),
                    "states": State.search([], order="name asc"),
                    "currency_symbol": company.currency_id.symbol or "",
                }
            )
        except Exception as e:
            _logger.warning("Could not inject portal expense create context: %s", e)
        return response

    @http.route(
        ["/my/expenses/create"],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
        csrf=True,
    )
    def portal_create_expense(self, **post):  # noqa: C901
        employee = self._portal_employee()
        company = request.env.company

        partner = employee.sudo().work_contact_id
        if partner:
            ok_privacy = self._create_privacy_consents(post, partner)
            if not ok_privacy:
                return request.redirect("/my/expenses?create_error=1")

        partner_ssn = (post.get("partner_ssn") or "").strip()
        partner_street = (post.get("partner_street") or "").strip()
        partner_street2 = (post.get("partner_street2") or "").strip()
        partner_zip = (post.get("partner_zip") or "").strip()
        partner_city = (post.get("partner_city") or "").strip()
        partner_country_id = self._to_int(post.get("partner_country_id"), 0)
        partner_state_id = self._to_int(post.get("partner_state_id"), 0)

        partner_iban = (post.get("partner_iban") or "").strip()
        if partner_iban:
            try:
                partner = employee.sudo().work_contact_id
                if partner:
                    Bank = request.env["res.partner.bank"].sudo()

                    # Try to update existing bank account linked to employee
                    bank = employee.sudo().bank_account_id
                    if bank:
                        bank.write({"acc_number": partner_iban})
                    else:
                        # Create new bank account for partner and link to employee
                        new_bank = Bank.create(
                            {
                                "partner_id": partner.id,
                                "acc_number": partner_iban,
                            }
                        )
                        employee.sudo().write({"bank_account_id": new_bank.id})
            except Exception as e:
                _logger.exception("Saving IBAN failed: %s", e)
                request.env.cr.rollback()
                return request.redirect("/my/expenses?create_error=1")

        if partner_ssn or any(
            [
                partner_street,
                partner_street2,
                partner_zip,
                partner_city,
                partner_country_id,
                partner_state_id,
            ]
        ):
            try:
                partner = employee.sudo().work_contact_id
                if partner:
                    vals_partner = {
                        "street": partner_street or False,
                        "street2": partner_street2 or False,
                        "zip": partner_zip or False,
                        "city": partner_city or False,
                        "country_id": partner_country_id or False,
                        "state_id": partner_state_id or False,
                    }
                    if partner_ssn:
                        vals_partner["social_security_number"] = partner_ssn
                    partner.sudo().write(vals_partner)
            except Exception as e:
                _logger.exception("Saving partner details failed: %s", e)
                request.env.cr.rollback()
                return request.redirect("/my/expenses?create_error=1")

        form = request.httprequest.form
        indices = form.getlist("line_idx") or []
        indices = [str(i).strip() for i in indices if str(i).strip()]

        if not indices:
            _logger.warning("PORTAL EXPENSE CREATE: no line_idx provided")
            return request.redirect("/my/expenses?create_error=1")

        allowed_products = self._allowed_products(company)
        allowed_product_ids = set(allowed_products.ids)

        expense_vals_list = []
        kept_indices = []
        attachments_by_index = {}

        any_invalid = False
        invalid_indices = []

        for idx in indices:
            raw_name = form.get(f"line_name_{idx}")
            raw_product = form.get(f"line_product_id_{idx}")
            raw_date = form.get(f"line_date_{idx}")
            raw_notes = form.get(f"line_description_{idx}")
            raw_qty = form.get(f"line_quantity_{idx}")
            raw_unit = form.get(f"line_price_unit_{idx}")

            line_name = (raw_name or "").strip()
            line_product_id = self._to_int(raw_product, 0)
            line_notes = (raw_notes or "").strip()
            line_date = self._normalize_date(raw_date)

            try:
                line_quantity = self._to_float(raw_qty, default=1.0)
            except Exception:
                line_quantity = 0.0

            try:
                line_price_unit = self._to_float(raw_unit, default=0.0)
            except Exception:
                line_price_unit = 0.0

            # Skip fully empty lines
            is_empty = (
                not line_name
                and not line_product_id
                and (not raw_date or not str(raw_date).strip())
                and not line_notes
                and (raw_qty in (None, "", False) or str(raw_qty).strip() in ("", "0"))
                and (
                    raw_unit in (None, "", False) or str(raw_unit).strip() in ("", "0")
                )
            )
            if is_empty:
                continue

            # Validations
            if (
                not line_name
                or not line_product_id
                or line_product_id not in allowed_product_ids
            ):
                any_invalid = True
                invalid_indices.append(idx)
                _logger.warning(
                    "PORTAL EXPENSE LINE INVALID idx=%s (name=%r product_id=%s allowed=%s)",  # noqa E501
                    idx,
                    line_name,
                    line_product_id,
                    (line_product_id in allowed_product_ids),
                )
                continue

            if line_quantity <= 0 or line_price_unit <= 0:
                any_invalid = True
                invalid_indices.append(idx)
                _logger.warning(
                    "PORTAL EXPENSE LINE INVALID AMOUNTS idx=%s qty=%s unit=%s",
                    idx,
                    line_quantity,
                    line_price_unit,
                )
                continue

            total_amount_currency = line_price_unit * line_quantity

            expense_vals_list.append(
                {
                    "name": line_name,
                    "date": line_date,
                    "employee_id": employee.id,
                    "company_id": company.id,
                    "product_id": line_product_id,
                    "quantity": line_quantity,
                    "price_unit": line_price_unit,  # requested: store unit price
                    "description": line_notes or False,
                    "currency_id": company.currency_id.id,
                    "total_amount_currency": total_amount_currency,
                    # IMPORTANT: UI removed Paid-by, but model often needs this
                    "payment_mode": "own_account",
                }
            )
            kept_indices.append(idx)

            uploads = request.httprequest.files.getlist(f"receipt_{idx}") or []
            uploads = [u for u in uploads if getattr(u, "filename", None)]
            attachments_by_index[idx] = self._create_attachments(uploads)

        if not expense_vals_list or any_invalid:
            _logger.warning(
                "PORTAL EXPENSE CREATE: aborting (any_invalid=%s, vals=%s)",
                any_invalid,
                len(expense_vals_list),
            )
            return request.redirect("/my/expenses?create_error=1")

        try:
            expenses = request.env["hr.expense"].sudo().create(expense_vals_list)
        except Exception as e:
            _logger.exception("Creating expense lines failed: %s", e)
            request.env.cr.rollback()
            return request.redirect("/my/expenses?create_error=1")

        try:
            for expense, idx in zip(expenses, kept_indices):  # noqa B905
                atts = attachments_by_index.get(idx)
                if atts and atts.exists():
                    atts.write({"res_id": expense.id})
                    # attach_document accepts multiple IDs
                    expense.sudo().attach_document(attachment_ids=atts.ids)
        except Exception as e:
            _logger.exception("Attaching receipts failed: %s", e)
            request.env.cr.rollback()
            return request.redirect("/my/expenses?create_error=1")

        try:
            expenses.sudo().action_submit_expenses()
        except Exception as e:
            _logger.exception("Submitting expenses into sheet failed: %s", e)
            request.env.cr.rollback()
            return request.redirect("/my/expenses?create_error=1")

        return request.redirect("/my/expenses?create_ok=1")
