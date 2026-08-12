import logging
from collections import OrderedDict

from odoo import _, http
from odoo.http import request
from odoo.osv.expression import AND, OR

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager

_logger = logging.getLogger(__name__)


class HrSkillPortal(CustomerPortal):
    """Portal controller that provides a modern listing
    for hr.employee.skill records (with sidebar lists)."""

    # -------------------------
    # Top-level helpers (no nested defs)
    # -------------------------

    def _split_multi(self, term):
        """
        Split a user term into multiple values.
        - Supports comma, semicolon or pipe as separators.
        - Trims whitespace and drops empties.
        """
        if not term:
            return []
        raw = []
        for sep in [",", ";", "|"]:
            if sep in term:
                raw = [p.strip() for p in term.split(sep)]
                break
        if not raw:
            raw = [term.strip()]
        return [p for p in raw if p]

    def _get_multi_ids(self, key):
        """
        Read a list of integer ids from GET params (key may appear multiple times).
        Also supports comma-separated values in a single parameter.
        """
        args = request.httprequest.args
        values = []
        for v in args.getlist(key):
            if not v:
                continue
            parts = self._split_multi(v)
            for p in parts:
                try:
                    values.append(int(p))
                except Exception as e:
                    _logger.warning(e)
                    pass
        # de-duplicate keeping order
        seen = set()
        out = []
        for vid in values:
            if vid not in seen:
                out.append(vid)
                seen.add(vid)
        return out

    def _group_key(self, rec, gfield):
        """
        Compute the grouping key id for a record given a (possibly dotted) field name.
        """
        cur = rec
        for part in gfield.split("."):
            cur = getattr(cur, part)
        return cur.id if cur else 0

    def _group_records(self, records, groupby):
        """
        Group records by the configured groupby key while preserving order.
        - Supports dotted fields via getattr chain.
        - Returns a list of recordsets (groups).
        """
        mapping = self._groupby_mapping()
        gfield = mapping.get(groupby)
        if not gfield:
            return [records] if records else []

        buckets = {}
        ordered_keys = []
        for r in records:
            k = self._group_key(r, gfield)
            if k not in buckets:
                buckets[k] = request.env["hr.employee.skill"]
                ordered_keys.append(k)
            buckets[k] |= r
        return [buckets[k] for k in ordered_keys]

    # -------------------------
    # Searchbar config
    # -------------------------

    def _skill_searchbar_sortings(self):
        """
        Define sorting options for the searchbar.
        - Keys map to labels and SQL order strings.
        - 'sequence' controls display order in the UI.
        """
        return {
            "date": {"label": _("Newest"), "order": "create_date desc", "sequence": 1},
            "employee": {
                "label": _("Employee"),
                "order": "employee_id, skill_type_id, skill_id",
                "sequence": 2,
            },
            "skill": {
                "label": _("Skill"),
                "order": "skill_type_id, skill_id, skill_level_id",
                "sequence": 3,
            },
            "level": {
                "label": _("Level"),
                "order": "skill_level_id desc",
                "sequence": 4,
            },
        }

    def _skill_searchbar_groupby(self):
        """
        Define group-by options for the searchbar.
        - Keys map to UI labels and a simple display order.
        - Actual field mapping is handled by _groupby_mapping().
        """
        return {
            "none": {"input": "none", "label": _("None"), "order": 1},
            "employee": {"input": "employee", "label": _("Employee"), "order": 2},
            "department": {"input": "department", "label": _("Department"), "order": 3},
            "type": {"input": "type", "label": _("Skill Type"), "order": 4},
            "skill": {"input": "skill", "label": _("Skill"), "order": 5},
            "level": {"input": "level", "label": _("Level"), "order": 6},
        }

    def _skill_searchbar_inputs(self):
        """
        Define search scopes (search_in) for the searchbar.
        - Keep labels concise; order controls display order.
        """
        return {
            "all": {"input": "all", "label": _("Search in All"), "order": 1},
            "employee": {
                "input": "employee",
                "label": _("Search in Employee"),
                "order": 2,
            },
            "department": {
                "input": "department",
                "label": _("Search in Department"),
                "order": 3,
            },
            "skill": {"input": "skill", "label": _("Search in Skill"), "order": 4},
            "type": {"input": "type", "label": _("Search in Skill Type"), "order": 5},
            "level": {"input": "level", "label": _("Search in Level"), "order": 6},
        }

    def _groupby_mapping(self):
        """
        Map group-by keys to actual model fields.
        """
        return {
            "employee": "employee_id",
            "department": "department_id",
            "type": "skill_type_id",
            "skill": "skill_id",
            "level": "skill_level_id",
        }

    def _order_with_groupby(self, order, groupby):
        """
        Build an order clause that honors grouping.
        - Prepends the group-by field to the order when grouping is active.
        - Falls back to the provided order if no grouping is set.
        """
        field = self._groupby_mapping().get(groupby)
        return f"{field}, {order}" if field else order

    def _build_basic_search_domain(self, search_in, term):
        """
        Build a domain for simple free-text search.
        - Limits search to the selected scope
          (employee/skill/type/level/department) or 'all'.
        - Uses ilike on human-readable names for better UX.
        """
        parts = []
        if search_in in ("all", "employee"):
            parts.append([("employee_id.name", "ilike", term)])
        if search_in in ("all", "department"):
            parts.append([("department_id.name", "ilike", term)])
        if search_in in ("all", "skill"):
            parts.append([("skill_id.name", "ilike", term)])
        if search_in in ("all", "type"):
            parts.append([("skill_type_id.name", "ilike", term)])
        if search_in in ("all", "level"):
            parts.append([("skill_level_id.name", "ilike", term)])
        return OR(parts) if parts else []

    # -------------------------
    # Core filter helper for skills & levels (AND logic)
    # -------------------------

    def _apply_skill_level_filters(
        self, Skill, base_domain, selected_skill_ids, selected_level_ids
    ):
        """
        Apply AND filters for selected skills and/or
        levels onto base_domain and return a new domain.

        AND semantics:
        - skills + levels: employee must have EACH selected skill
          at ANY of the selected levels (at least one allowed level per skill).
          Result rows are then limited to those skills and those levels.
        - skills only: employee must have EACH selected skill (any level).
          Rows limited to selected skills.
        - levels only: employee must have EACH selected level (with any skill).
          Rows limited to selected levels.
        - none selected: base_domain unchanged.
        """
        domain = list(base_domain) if base_domain else []

        if selected_skill_ids and selected_level_ids:
            rg_rows = Skill.read_group(
                domain=AND(
                    [
                        domain,
                        [
                            ("skill_id", "in", selected_skill_ids),
                            ("skill_level_id", "in", selected_level_ids),
                        ],
                    ]
                ),
                fields=["employee_id", "skill_id", "skill_level_id"],
                groupby=["employee_id", "skill_id", "skill_level_id"],
                lazy=False,
            )
            emp_to_ok_skills = {}
            for row in rg_rows:
                emp_id = row["employee_id"] and row["employee_id"][0]
                skl_id = row["skill_id"] and row["skill_id"][0]
                lvl_id = row["skill_level_id"] and row["skill_level_id"][0]
                if not (emp_id and skl_id and lvl_id):
                    continue
                # mark the skill as present at an allowed level
                emp_to_ok_skills.setdefault(emp_id, set()).add(skl_id)

            must_have = set(selected_skill_ids)
            ok_emp_ids = [
                e for e, sset in emp_to_ok_skills.items() if must_have.issubset(sset)
            ]

            domain = AND(
                [
                    domain,
                    [("employee_id", "in", ok_emp_ids or [0])],
                    [("skill_id", "in", selected_skill_ids)],
                    [("skill_level_id", "in", selected_level_ids)],
                ]
            )
            return domain

        if selected_skill_ids:
            rg_rows = Skill.read_group(
                domain=AND([domain, [("skill_id", "in", selected_skill_ids)]]),
                fields=["employee_id", "skill_id"],
                groupby=["employee_id", "skill_id"],
                lazy=False,
            )
            emp_to_skills = {}
            for row in rg_rows:
                emp_id = row["employee_id"] and row["employee_id"][0]
                skl_id = row["skill_id"] and row["skill_id"][0]
                if emp_id and skl_id:
                    emp_to_skills.setdefault(emp_id, set()).add(skl_id)

            must_have = set(selected_skill_ids)
            ok_emp_ids = [
                e for e, sset in emp_to_skills.items() if must_have.issubset(sset)
            ]

            domain = AND(
                [
                    domain,
                    [("employee_id", "in", ok_emp_ids or [0])],
                    [("skill_id", "in", selected_skill_ids)],
                ]
            )
            return domain

        if selected_level_ids:
            rg_rows = Skill.read_group(
                domain=AND([domain, [("skill_level_id", "in", selected_level_ids)]]),
                fields=["employee_id", "skill_level_id"],
                groupby=["employee_id", "skill_level_id"],
                lazy=False,
            )
            emp_to_levels = {}
            for row in rg_rows:
                emp_id = row["employee_id"] and row["employee_id"][0]
                lvl_id = row["skill_level_id"] and row["skill_level_id"][0]
                if emp_id and lvl_id:
                    emp_to_levels.setdefault(emp_id, set()).add(lvl_id)

            must_have_lvls = set(selected_level_ids)
            ok_emp_ids = [
                e for e, lset in emp_to_levels.items() if must_have_lvls.issubset(lset)
            ]

            domain = AND(
                [
                    domain,
                    [("employee_id", "in", ok_emp_ids or [0])],
                    [("skill_level_id", "in", selected_level_ids)],
                ]
            )
            return domain

        # nothing selected
        return domain

    # -------------------------
    # Value preparation
    # -------------------------

    def _prepare_skill_values(self, page, sortby, search, search_in, groupby):
        """
        Collect all values required by the template.
        - Adds sidebar data (skills, levels) and shows current selections.
        - Applies AND logic for selected skills/levels via _apply_skill_level_filters().

        Access is gated on hr.skills.portal.access. This is enforced twice:
        - Here, so a user without access skips the query pipeline entirely
          and the template renders its "access restricted" notice instead.
        - By the ir.rule records in security/hr_skills_frontend_security.xml,
          which grant base.group_portal real (non-sudo) read access to
          hr.employee.skill/hr.employee/hr.department/hr.skill/
          hr.skill.level/hr.skill.type only while the same grant is active
          — so this method never needs sudo() to read them.
        """
        values = self._prepare_portal_layout_values()
        Skill = request.env["hr.employee.skill"]

        Access = request.env["hr.skills.portal.access"]
        user = request.env.user
        has_access = Access.user_has_portal_skills_access(user)

        # Searchbar config is rendered above the has_access check in the
        # template, so it must be populated regardless of access.
        searchbar_sortings = dict(
            sorted(
                self._skill_searchbar_sortings().items(), key=lambda i: i[1]["sequence"]
            )
        )
        searchbar_inputs = self._skill_searchbar_inputs()
        searchbar_groupby = self._skill_searchbar_groupby()
        sortby = sortby if sortby in searchbar_sortings else "date"
        groupby = groupby if groupby in searchbar_groupby else "employee"

        values.update(
            {
                "page_name": "hr_employee_skill",
                "default_url": "/all/skills",
                "searchbar_sortings": searchbar_sortings,
                "searchbar_groupby": OrderedDict(
                    sorted(searchbar_groupby.items(), key=lambda i: i[1]["order"])
                ),
                "searchbar_inputs": OrderedDict(
                    sorted(searchbar_inputs.items(), key=lambda i: i[1]["order"])
                ),
                "search_in": search_in or "all",
                "search": search,
                "sortby": sortby,
                "groupby": groupby,
                "has_access": has_access,
            }
        )

        if not has_access:
            return values

        domain = []

        # Read selections from query
        selected_skill_ids = self._get_multi_ids("skill_ids")
        selected_level_ids = self._get_multi_ids("level_ids")

        order = self._order_with_groupby(searchbar_sortings[sortby]["order"], groupby)

        # Free text search
        if search:
            domain = AND(
                [domain, self._build_basic_search_domain(search_in or "all", search)]
            )

        # Apply skill/level AND-filters using a single helper
        domain = self._apply_skill_level_filters(
            Skill, domain, selected_skill_ids, selected_level_ids
        )

        # Fetch page of records
        total = Skill.search_count(domain)
        pager = portal_pager(
            url="/all/skills",
            url_args={
                "sortby": sortby,
                "groupby": groupby,
                "search_in": search_in,
                "search": search,
                "skill_ids": ",".join(map(str, selected_skill_ids))
                if selected_skill_ids
                else "",
                "level_ids": ",".join(map(str, selected_level_ids))
                if selected_level_ids
                else "",
            },
            total=total,
            page=page,
            step=self._items_per_page,
        )
        records = Skill.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )
        grouped_records = self._group_records(records, groupby)

        # Sidebar lists
        SkillM = request.env["hr.skill"]
        LevelM = request.env["hr.skill.level"]
        skills = SkillM.search([])
        levels = LevelM.search([])

        values.update(
            {
                "grouped_records": grouped_records,
                "pager": pager,
                # sidebar data + current selections
                "skills": skills,
                "levels": levels,
                "selected_skill_ids": selected_skill_ids,
                "selected_level_ids": selected_level_ids,
            }
        )
        return values

    # -------------------------
    # Routes
    # -------------------------

    @http.route(
        ["/all/skills", "/all/skills/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_all_skills(
        self, page=1, sortby=None, search=None, search_in="all", groupby=None, **kw
    ):
        """
        Route: render the skill listing page with a sidebar (skills + levels).
        - Supports pagination via /all/skills/page/<int:page>.
        - Accepts sortby, search, search_in, groupby, skill_ids, level_ids.
        """
        values = self._prepare_skill_values(page, sortby, search, search_in, groupby)
        return request.render("hr_skills_frontend.portal_all_skills", values)
