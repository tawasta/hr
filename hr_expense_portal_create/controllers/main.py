# -*- coding: utf-8 -*-

import base64
import logging
from datetime import date, datetime

from odoo import _, http
from odoo.http import request
from odoo.exceptions import ValidationError

from odoo.addons.hr_expense_portal.controllers.main import HrExpenseCustomerPortal

_logger = logging.getLogger(__name__)


class HrExpenseCustomerPortalCreate(HrExpenseCustomerPortal):

    def _portal_employee(self):
        employee = request.env.user.sudo().employee_id
        if not employee:
            raise ValidationError(_("The current user has no related employee. Please contact support."))
        return employee

    def _allowed_products(self, company):
        Product = request.env["product.product"].sudo()
        domain = [
            ("can_be_expensed", "=", True),
            "|", ("company_id", "=", False), ("company_id", "=", company.id),
        ]
        return Product.search(domain, order="name asc")

    def _to_float(self, value, default=0.0):
        if value in (None, "", False):
            return default
        if isinstance(value, str):
            value = value.replace(" ", "").replace(",", ".")
        return float(value)

    def _validate_payment_mode(self, payment_mode):
        if payment_mode not in ("own_account", "company_account"):
            return "own_account"
        return payment_mode

    def _create_attachment(self, upload):
        if not upload or not getattr(upload, "filename", False):
            return request.env["ir.attachment"].sudo()

        content = upload.read()
        if not content:
            return request.env["ir.attachment"].sudo()

        Attachment = request.env["ir.attachment"].sudo()
        att = Attachment.create({
            "name": upload.filename,
            "datas": base64.b64encode(content),
            "mimetype": upload.content_type,
            "res_model": "hr.expense",
            "res_id": 0,
        })
        return att

    def _normalize_date(self, raw_date):
        raw_date = (raw_date or "").strip()
        if not raw_date:
            return date.today().isoformat()

        for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
            try:
                return datetime.strptime(raw_date, fmt).date().isoformat()
            except ValueError:
                pass

        return date.today().isoformat()


    def portal_my_expenses(self, page=1, sortby="date", filterby="all",
                           search=None, search_in="all", groupby="none", **kw):
        response = super().portal_my_expenses(
            page=page,
            sortby=sortby,
            filterby=filterby,
            search=search,
            search_in=search_in,
            groupby=groupby,
            **kw
        )
        try:
            company = request.env.company
            response.qcontext["today_fi"] = date.today().strftime("%d.%m.%Y")  # dd.MM.yyyy
            response.qcontext["products"] = self._allowed_products(company)
            employee = self._portal_employee()
            partner = employee.sudo().work_contact_id
            bank = employee.sudo().bank_account_id

            response.qcontext.update({
                "employee": employee,
                "speaker_partner": partner,
                "speaker_iban": bank.acc_number if bank else "",
            })
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
    def portal_create_expense(self, **post):
        employee = self._portal_employee()
        company = request.env.company

        speaker_ssn = (post.get("speaker_ssn") or "").strip()
        if speaker_ssn:
            try:
                partner = employee.sudo().work_contact_id
                if partner:
                    # This triggers your res.partner create/write hook:
                    # -> encrypt + hash, and removes plaintext field from vals
                    partner.sudo().write({"social_security_number": speaker_ssn})
            except Exception as e:
                _logger.exception("Saving speaker SSN to partner failed: %s", e)
                request.env.cr.rollback()
                return request.redirect("/my/expenses?create_error=1")

        name = (post.get("name") or "").strip()
        product_id = int(post.get("product_id") or 0)
        expense_date = self._normalize_date(post.get("date"))
        payment_mode = self._validate_payment_mode((post.get("payment_mode") or "own_account").strip())
        description = (post.get("description") or "").strip()

        try:
            quantity = self._to_float(post.get("quantity"), default=1.0)
        except Exception:
            quantity = 0.0

        errors = []
        if not name:
            errors.append("name")
        if not product_id:
            errors.append("product_id")
        if quantity <= 0:
            errors.append("quantity")

        allowed_products = self._allowed_products(company)
        if product_id and product_id not in allowed_products.ids:
            errors.append("product_id")

        if errors:
            return request.redirect("/my/expenses?create_error=1")

        upload = post.get("receipt")
        attachment = self._create_attachment(upload)

        vals = {
            "name": name,
            "date": expense_date,
            "employee_id": employee.id,
            "company_id": company.id,
            "product_id": product_id,
            "quantity": quantity,
            "payment_mode": payment_mode,
            "description": description or False,
        }

        try:
            expense = request.env["hr.expense"].sudo().create(vals)
            if attachment and attachment.exists():
                attachment.write({"res_id": expense.id})
                expense.sudo().attach_document(attachment_ids=[attachment.id])
        except Exception as e:
            _logger.exception("Portal expense create failed: %s", e)
            request.env.cr.rollback()
            return request.redirect("/my/expenses?create_error=1")

        return request.redirect("/my/expenses?create_ok=1")
