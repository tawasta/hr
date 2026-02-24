from collections import OrderedDict
from operator import itemgetter

from dateutil.relativedelta import relativedelta

from odoo import _, fields, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.osv.expression import AND, OR
from odoo.tools import date_utils
from odoo.tools import groupby as groupbyelem

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class HrExpenseCustomerPortal(CustomerPortal):
    def _check_portal_expense_access(self):
        if not request.env.user.has_group(
            "hr_expense_portal.group_portal_expense_access"
        ):
            raise AccessError(_("Access Denied"))

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "expense_count" in counters:
            values["expense_count"] = request.env["hr.expense"].search_count([])
        if "expense_sheet_count" in counters:
            values["expense_sheet_count"] = request.env[
                "hr.expense.sheet"
            ].search_count([])
        return values

    def _expense_searchbar_sortings(self):
        return {
            "date": {"label": _("Newest"), "order": "date desc, id desc"},
            "amount": {"label": _("Amount"), "order": "total_amount desc, id desc"},
            "state": {"label": _("Status"), "order": "state asc, date desc"},
            "name": {"label": _("Description"), "order": "name asc, date desc"},
        }

    def _expense_searchbar_inputs(self):
        return {
            "all": {"input": "all", "label": _("Search in All")},
            "name": {"input": "name", "label": _("Search in Description")},
            "category": {"input": "category", "label": _("Search in Category")},
            "report": {"input": "report", "label": _("Search in Report")},
        }

    def _expense_searchbar_groupby(self):
        return {
            "none": {"input": "none", "label": _("None")},
            "state": {"input": "state", "label": _("Status")},
            "month": {"input": "month", "label": _("Month")},
            "report": {"input": "report", "label": _("Expense Report")},
            "category": {"input": "category", "label": _("Category")},
        }

    def _expense_groupby_mapping(self):
        return {
            "state": "state",
            "report": "sheet_id",
            "category": "product_id",
            "month": "date:month",
        }

    def _expense_get_search_domain(self, search_in, search):
        dom = []
        if not search:
            return dom

        if search_in in ("name", "all"):
            dom = OR([dom, [("name", "ilike", search)]])
        if search_in in ("category", "all"):
            dom = OR([dom, [("product_id.display_name", "ilike", search)]])
        if search_in in ("report", "all"):
            dom = OR([dom, [("sheet_id.name", "ilike", search)]])
        return dom

    def _expense_searchbar_filters(self):
        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)

        return OrderedDict(
            [
                ("all", {"label": _("All"), "domain": []}),
                (
                    "to_report",
                    {"label": _("To Report"), "domain": [("state", "=", "draft")]},
                ),
                (
                    "to_submit",
                    {"label": _("To Submit"), "domain": [("state", "=", "reported")]},
                ),
                (
                    "submitted",
                    {"label": _("Submitted"), "domain": [("state", "=", "submitted")]},
                ),
                (
                    "approved",
                    {"label": _("Approved"), "domain": [("state", "=", "approved")]},
                ),
                ("done", {"label": _("Done"), "domain": [("state", "=", "done")]}),
                (
                    "refused",
                    {"label": _("Refused"), "domain": [("state", "=", "refused")]},
                ),
                ("today", {"label": _("Today"), "domain": [("date", "=", today)]}),
                (
                    "this_month",
                    {
                        "label": _("This month"),
                        "domain": [
                            ("date", ">=", date_utils.start_of(today, "month")),
                            ("date", "<=", date_utils.end_of(today, "month")),
                        ],
                    },
                ),
                (
                    "last_month",
                    {
                        "label": _("Last month"),
                        "domain": [
                            ("date", ">=", date_utils.start_of(last_month, "month")),
                            ("date", "<=", date_utils.end_of(last_month, "month")),
                        ],
                    },
                ),
                (
                    "this_quarter",
                    {
                        "label": _("This quarter"),
                        "domain": [
                            ("date", ">=", quarter_start),
                            ("date", "<=", quarter_end),
                        ],
                    },
                ),
                (
                    "this_year",
                    {
                        "label": _("This year"),
                        "domain": [
                            ("date", ">=", date_utils.start_of(today, "year")),
                            ("date", "<=", date_utils.end_of(today, "year")),
                        ],
                    },
                ),
                (
                    "last_year",
                    {
                        "label": _("Last year"),
                        "domain": [
                            ("date", ">=", date_utils.start_of(last_year, "year")),
                            ("date", "<=", date_utils.end_of(last_year, "year")),
                        ],
                    },
                ),
            ]
        )

    @http.route(
        ["/my/expenses", "/my/expenses/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
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
        self._check_portal_expense_access()
        Expense = request.env["hr.expense"]

        values = self._prepare_portal_layout_values()
        step = 50

        searchbar_sortings = self._expense_searchbar_sortings()
        searchbar_inputs = self._expense_searchbar_inputs()
        searchbar_groupby = self._expense_searchbar_groupby()
        searchbar_filters = self._expense_searchbar_filters()

        sortby = sortby or "date"
        order = searchbar_sortings.get(sortby, searchbar_sortings["date"])["order"]

        filterby = filterby or "all"
        domain = searchbar_filters.get(filterby, searchbar_filters["all"])["domain"]

        if search and search_in:
            domain = AND([domain, self._expense_get_search_domain(search_in, search)])

        total = Expense.search_count(domain)

        pager = portal_pager(
            url="/my/expenses",
            url_args={
                "sortby": sortby,
                "filterby": filterby,
                "search": search,
                "search_in": search_in,
                "groupby": groupby,
            },
            total=total,
            page=page,
            step=step,
        )

        expenses = Expense.search(
            domain, order=order, limit=step, offset=pager["offset"]
        )

        rg_total = Expense._read_group(domain, aggregates=["total_amount:sum"])
        total_amount_sum = rg_total[0][0] if rg_total else 0.0

        grouped_expenses = []
        if groupby and groupby != "none":
            mapping = self._expense_groupby_mapping()
            gb = mapping.get(groupby)

            if gb == "date:month":
                rg = Expense._read_group(
                    domain, ["date:month"], ["total_amount:sum", "id:recordset"]
                )
                grouped_expenses = [(records, amount) for _key, amount, records in rg]
            else:
                rg = Expense._read_group(domain, [gb], ["total_amount:sum"])
                amounts_by_key = {}
                for key, amount in rg:
                    amounts_by_key[key.id if hasattr(key, "id") else key] = amount

                for k, g in groupbyelem(expenses, itemgetter(gb)):
                    kk = k.id if hasattr(k, "id") else k
                    grouped_expenses.append(
                        (Expense.concat(*g), amounts_by_key.get(kk, 0.0))
                    )
        else:
            grouped_expenses = [(expenses, total_amount_sum)] if expenses else []

        values.update(
            {
                "page_name": "expense",
                "default_url": "/my/expenses",
                "pager": pager,
                "expenses": expenses,
                "grouped_expenses": grouped_expenses,
                "total_amount_sum": total_amount_sum,
                "searchbar_sortings": searchbar_sortings,
                "searchbar_filters": searchbar_filters,
                "searchbar_inputs": searchbar_inputs,
                "searchbar_groupby": searchbar_groupby,
                "sortby": sortby,
                "filterby": filterby,
                "search": search,
                "search_in": search_in,
                "groupby": groupby,
            }
        )
        return request.render("hr_expense_portal.portal_my_expenses", values)

    @http.route(
        ["/my/expenses/<int:expense_id>"], type="http", auth="user", website=True
    )
    def portal_my_expense(self, expense_id, **kw):
        self._check_portal_expense_access()
        try:
            expense = request.env["hr.expense"].browse(expense_id)
            if not expense.exists():
                raise MissingError()
            expense.check_access_rights("read")
            expense.check_access_rule("read")
        except (AccessError, MissingError):
            return request.redirect("/my")

        Attachment = request.env["ir.attachment"].sudo()
        attachments = Attachment.search(
            [
                ("res_model", "=", "hr.expense"),
                ("res_id", "=", expense.id),
            ]
        )

        values = self._prepare_portal_layout_values()
        values.update(
            {
                "page_name": "expense_detail",
                "expense": expense,
                "attachments": attachments,
            }
        )
        return request.render("hr_expense_portal.portal_my_expense", values)

    def _sheet_searchbar_sortings(self):
        return {
            "date": {"label": "Newest", "order": "accounting_date desc, id desc"},
            "name": {"label": "Name", "order": "name asc, id desc"},
            "state": {"label": "Status", "order": "state asc, accounting_date desc"},
            "amount": {"label": "Amount", "order": "total_amount desc, id desc"},
        }

    def _sheet_searchbar_inputs(self):
        return {
            "all": {"input": "all", "label": "Search in All"},
            "name": {"input": "name", "label": "Search in Name"},
        }

    def _sheet_get_search_domain(self, search_in, search):
        dom = []
        if not search:
            return dom
        if search_in in ("name", "all"):
            dom = OR([dom, [("name", "ilike", search)]])
        return dom

    def _sheet_searchbar_filters(self):
        return OrderedDict(
            [
                ("all", {"label": "All", "domain": []}),
                (
                    "to_submit",
                    {"label": "To Submit", "domain": [("state", "=", "draft")]},
                ),
                (
                    "submitted",
                    {"label": "Submitted", "domain": [("state", "=", "submit")]},
                ),
                (
                    "approved",
                    {"label": "Approved", "domain": [("state", "=", "approve")]},
                ),
                ("posted", {"label": "Posted", "domain": [("state", "=", "post")]}),
                ("done", {"label": "Done", "domain": [("state", "=", "done")]}),
                ("refused", {"label": "Refused", "domain": [("state", "=", "cancel")]}),
            ]
        )

    @http.route(
        ["/my/expense-reports", "/my/expense-reports/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_expense_reports(
        self, page=1, sortby="date", filterby="all", search=None, search_in="all", **kw
    ):
        self._check_portal_expense_access()
        Sheet = request.env["hr.expense.sheet"]

        values = self._prepare_portal_layout_values()
        step = 30

        searchbar_sortings = self._sheet_searchbar_sortings()
        searchbar_inputs = self._sheet_searchbar_inputs()
        searchbar_filters = self._sheet_searchbar_filters()

        sortby = sortby or "date"
        order = searchbar_sortings.get(sortby, searchbar_sortings["date"])["order"]

        filterby = filterby or "all"
        domain = searchbar_filters.get(filterby, searchbar_filters["all"])["domain"]

        if search and search_in:
            domain = AND([domain, self._sheet_get_search_domain(search_in, search)])

        total = Sheet.search_count(domain)

        pager = portal_pager(
            url="/my/expense-reports",
            url_args={
                "sortby": sortby,
                "filterby": filterby,
                "search": search,
                "search_in": search_in,
            },
            total=total,
            page=page,
            step=step,
        )

        sheets = Sheet.search(domain, order=order, limit=step, offset=pager["offset"])

        values.update(
            {
                "page_name": "expense_sheet",
                "default_url": "/my/expense-reports",
                "pager": pager,
                "sheets": sheets,
                "searchbar_sortings": searchbar_sortings,
                "searchbar_filters": searchbar_filters,
                "searchbar_inputs": searchbar_inputs,
                "sortby": sortby,
                "filterby": filterby,
                "search": search,
                "search_in": search_in,
            }
        )
        return request.render("hr_expense_portal.portal_my_expense_reports", values)
