from odoo import http, _
from odoo.http import request
from odoo.osv.expression import AND
import logging

_logger = logging.getLogger(__name__)

SECT_SKILLS = "skills"
SECT_PROFILE = "profile"
SECT_SKILLS_ALL = "skills_all"
_UI_MODES = ("single", "type_all")


def _employee_of_current_user():
    """Return hr.employee of the logged-in user or False."""
    user = request.env.user.sudo()
    return user.employee_id or request.env["hr.employee"].sudo().search(
        [("user_id", "=", user.id)], limit=1
    )


def _restrict_to_employee(emp):
    """Domain: only given employee."""
    return [("employee_id", "=", emp.id)]


def _ui_mode(env):
    """UI mode from system parameter."""
    mode = (
        (
            env["ir.config_parameter"]
            .sudo()
            .get_param("hr_skills_frontend.mode", "single")
            or ""
        )
        .strip()
        .lower()
    )
    return mode if mode in _UI_MODES else "single"


def _collect_section_rows(emp, schema):
    """Rows for skills list according to schema."""
    for sec in schema:
        if sec["key"] == SECT_SKILLS:
            Model = request.env[sec["model"]].sudo()
            recs = Model.search(_restrict_to_employee(emp), order="id desc", limit=200)
            rows = []
            for r in recs:
                row = {"id": r.id}
                for col in sec["list_columns"]:
                    val = getattr(r, col["name"])
                    row[col["name"]] = (
                        val.display_name if col.get("type") == "m2o" else val
                    ) or ""
                rows.append(row)
            return {SECT_SKILLS: rows}
    return {SECT_SKILLS: []}


def _profile_values(emp):
    """Profile fields + derived counters."""
    emp = emp.sudo()
    return {
        "consulting_since": emp.consulting_since.isoformat()
        if emp.consulting_since
        else "",
        "strategy_since": emp.strategy_since.isoformat() if emp.strategy_since else "",
        "bio": emp.bio or "",
        "consulting_years": emp.consulting_years,
        "strategy_years": emp.strategy_years,
    }


class PortalSkillProfileController(http.Controller):
    """Portal modal for 'My skills' and 'Profile'."""

    def _schema(self, employee):
        """Section/field schema for the modal."""
        return [
            {
                "key": SECT_SKILLS,
                "title": _("Skills"),
                "model": "hr.employee.skill",
                "defaults": {"employee_id": employee.id},
                "list_columns": [
                    {"name": "skill_type_id", "label": _("Skill Type"), "type": "m2o"},
                    {"name": "skill_id", "label": _("Skill"), "type": "m2o"},
                    {"name": "skill_level_id", "label": _("Level"), "type": "m2o"},
                    {"name": "level_progress", "label": _("Progress (%)")},
                ],
                "fields": [
                    {
                        "name": "skill_type_id",
                        "label": _("Skill Type"),
                        "type": "many2one",
                        "comodel": "hr.skill.type",
                        "required": True,
                    },
                    {
                        "name": "skill_id",
                        "label": _("Skill"),
                        "type": "many2one",
                        "comodel": "hr.skill",
                        "required": True,
                        "depends_on": "skill_type_id",
                    },
                    {
                        "name": "skill_level_id",
                        "label": _("Level"),
                        "type": "many2one",
                        "comodel": "hr.skill.level",
                        "required": True,
                        "depends_on": "skill_type_id",
                    },
                ],
            },
            {
                "key": SECT_PROFILE,
                "title": _("Profile"),
                "model": "hr.employee",
                "fields": [
                    {
                        "name": "consulting_since",
                        "label": _("Consulting since"),
                        "type": "date",
                    },
                    {
                        "name": "strategy_since",
                        "label": _("Strategy work since"),
                        "type": "date",
                    },
                    {"name": "bio", "label": _("About me"), "type": "text"},
                ],
            },
        ]

    def _collect_initial_options(self, emp, schema):
        """Initial M2O options for non-dependent fields in skills."""
        opts = {}
        for sec in schema:
            if sec["key"] != SECT_SKILLS:
                continue
            sec_opts = {}
            for f in sec["fields"]:
                if f.get("type") == "many2one" and not f.get("depends_on"):
                    sec_opts[f["name"]] = self._m2o_options(emp, f, {})
            opts[SECT_SKILLS] = sec_opts
        return opts

    def _render_modal_body(self, emp, schema):
        """Render modal body with rows, options and profile values."""
        return request.env["ir.ui.view"]._render_template(
            "hr_skills_frontend.portal_skills_modal_body",
            {
                "schema": schema,
                "section_rows": _collect_section_rows(emp, schema),
                "initial_options": self._collect_initial_options(emp, schema),
                "profile_values": _profile_values(emp),
                "csrf_token": request.csrf_token(),
                "ui_mode": _ui_mode(request.env),
            },
        )

    @http.route(
        "/my/skills_modal/body", type="http", auth="user", website=True, methods=["GET"]
    )
    def skills_modal_body(self, **_kw):
        """Return modal body fragment."""
        emp = _employee_of_current_user()
        if not emp:
            return request.render(
                "hr_skills_frontend.portal_skills_modal_body_error", {}
            )
        return self._render_modal_body(emp, self._schema(emp))

    @http.route(
        "/my/skills_modal/m2o_options",
        type="json",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def m2o_options(self, section_key=None, field_name=None, context_values=None):
        """Return (id, name) options for a dependent many2one field."""
        emp = _employee_of_current_user()
        if not emp:
            return []
        sec = next((s for s in self._schema(emp) if s["key"] == section_key), None)
        if not sec:
            return []
        fdef = next(
            (
                f
                for f in sec["fields"]
                if f["name"] == field_name and f["type"] == "many2one"
            ),
            None,
        )
        return self._m2o_options(emp, fdef, context_values or {}) if fdef else []

    def _m2o_options(self, employee, fdef, ctx_vals):
        """Compute domain and return options for a given many2one field."""
        Model = request.env[fdef["comodel"]].sudo()
        domain, ctx = [], {}

        dep = fdef.get("depends_on")
        stid = int(ctx_vals.get(dep) or 0) if dep else 0
        if dep and not stid:
            return []
        if stid:
            domain.append(("skill_type_id", "=", stid))
        if "active" in Model._fields:
            domain.append(("active", "=", True))

        if fdef["comodel"] == "hr.skill":
            ctx["from_skill_dropdown"] = True
            if ctx_vals.get("exclude_existing") and stid:
                taken = (
                    request.env["hr.employee.skill"]
                    .sudo()
                    .search(
                        [
                            ("employee_id", "=", employee.id),
                            ("skill_type_id", "=", stid),
                        ]
                    )
                    .mapped("skill_id")
                    .ids
                )
                if taken:
                    domain.append(("id", "not in", taken))
        elif fdef["comodel"] == "hr.skill.level":
            ctx["from_skill_level_dropdown"] = True

        return [
            (r.id, r.display_name)
            for r in Model.with_context(**ctx).search(domain, limit=2000)
        ]

    def _apply_deletions(self, employee, delete_map):
        """Delete selected skills of current employee."""
        if not delete_map or not isinstance(delete_map, dict):
            return
        ids = delete_map.get(SECT_SKILLS) or []
        if not ids:
            return
        try:
            Model = request.env["hr.employee.skill"].sudo()
            recs = Model.search(
                AND([_restrict_to_employee(employee), [("id", "in", ids)]])
            )
            if recs:
                recs.unlink()
        except Exception as e:
            _logger.warning("Delete failed for hr.employee.skill ids=%s: %s", ids, e)
            request.env.cr.rollback()

    def _save_profile(self, emp, sec, prof_payload):
        """Write allowed profile fields to hr.employee."""
        if not sec:
            return {"ok": False, "error": "invalid_section"}
        allowed = {f["name"] for f in sec["fields"]}
        raw = prof_payload or {}
        vals = {
            n: (
                raw.get(n) or False
                if n.endswith("_since")
                else (raw.get(n) or "" if n == "bio" else raw.get(n))
            )
            for n in allowed
        }
        emp.sudo().write(vals)
        return {"ok": True}

    def _save_single_skill(self, emp, sec, raw_vals):
        """Create single hr.employee.skill unless duplicate or required missing."""
        if not sec:
            return {"ok": False, "error": "invalid_section"}
        vals = dict(sec.get("defaults", {}))
        for f in sec["fields"]:
            n = f["name"]
            vals[n] = int((raw_vals or {}).get(n) or 0) or False
            if f.get("required") and not vals[n]:
                return {"ok": False, "error": "required"}
        vals["employee_id"] = emp.id
        if vals.get("skill_id"):
            exists = (
                request.env["hr.employee.skill"]
                .sudo()
                .search_count(
                    [("employee_id", "=", emp.id), ("skill_id", "=", vals["skill_id"])]
                )
            )
            if not exists:
                request.env[sec["model"]].sudo().create(vals)
        return {"ok": True}

    def _save_skills_all(self, emp, items):
        """Bulk-create skills with chosen levels; skip existing."""
        items = items or []
        existing = set(
            request.env["hr.employee.skill"]
            .sudo()
            .search([("employee_id", "=", emp.id)])
            .mapped("skill_id")
            .ids
        )
        to_create = []
        for it in items:
            try:
                stid = int(it.get("skill_type_id") or 0)
                sid = int(it.get("skill_id") or 0)
                lid = int(it.get("skill_level_id") or 0)
            except Exception:
                continue
            if not (stid and sid and lid) or sid in existing:
                continue
            to_create.append(
                {
                    "employee_id": emp.id,
                    "skill_type_id": stid,
                    "skill_id": sid,
                    "skill_level_id": lid,
                    "level_progress": 0,
                }
            )
        if to_create:
            request.env["hr.employee.skill"].sudo().create(to_create)
            return {"ok": True}
        return {"ok": False, "error": "required"}

    @http.route(
        "/my/skills_modal/save",
        type="json",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def skills_modal_save(self, **payload):
        """Save profile/skills, apply deletions, and return fresh modal body."""
        emp = _employee_of_current_user()
        if not emp:
            return {"ok": False, "error": "no_employee"}

        try:
            self._apply_deletions(emp, payload.get("delete_map") or {})
        except Exception as e:
            _logger.warning("Delete during save failed: %s", e)
            request.env.cr.rollback()

        section_key = (payload.get("section_key") or "").strip()
        schema = self._schema(emp)
        sec = next((s for s in schema if s["key"] == section_key), None)

        try:
            if section_key == SECT_PROFILE:
                res = self._save_profile(emp, sec, payload.get("profile"))
            elif section_key == SECT_SKILLS:
                res = self._save_single_skill(emp, sec, payload.get("skills"))
            elif section_key == SECT_SKILLS_ALL:
                res = self._save_skills_all(emp, payload.get("skills_all_items"))
            else:
                res = {"ok": True}
            if not res.get("ok"):
                return res
        except Exception as e:
            _logger.exception("Save failed in section %s: %s", section_key, e)
            request.env.cr.rollback()
            return {"ok": False, "error": "save_failed"}

        try:
            body_html = self._render_modal_body(emp, schema)
        except Exception as e:
            _logger.exception("Rendering refreshed modal body failed: %s", e)
            return {"ok": False, "error": "render_failed"}

        return {"ok": True, "body_html": body_html}
