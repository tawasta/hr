from odoo import http, _
from odoo.http import request
from odoo.osv.expression import AND
import json
import logging

_logger = logging.getLogger(__name__)

# ---------- Apufunktiot ----------

def _employee_of_current_user():
    """Palauta kirjautuneen käyttäjän työntekijä (hr.employee) tai False."""
    user = request.env.user.sudo()
    emp = user.employee_id
    if not emp:
        emp = (
            request.env["hr.employee"]
            .sudo()
            .search([("user_id", "=", user.id)], limit=1)
        )
    return emp

def _restrict_to_employee(emp):
    """Domain, joka rajaa hakua vain tiettyyn työntekijään."""
    return [("employee_id", "=", emp.id)]

# ---------- Kontrolleri ----------

class PortalSkillProfileController(http.Controller):
    """
    Portal: "My skills" -modaali + "Profile" -osio
    """

    # ---- SKEEMA: kuvaa modaalin osiot ----
    def _schema(self, employee):
        return [
            {
                "key": "skills",
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
                "key": "profile",
                "title": _("Profile"),
                "model": "hr.employee",
                "fields": [
                    {"name": "consulting_since", "label": _("Consulting since"), "type": "date"},
                    {"name": "strategy_since", "label": _("Strategy work since"), "type": "date"},
                    {"name": "bio", "label": _("About me"), "type": "text"},
                ],
            },
        ]

    # ---- GET: Rakenna modal-body (lista + initial options + profile values) ----
    @http.route(
        "/my/skills_modal/body", type="http", auth="user", website=True, methods=["GET"]
    )
    def skills_modal_body(self, **kw):
        emp = _employee_of_current_user()
        if not emp:
            return request.render(
                "hr_skills_frontend.portal_skills_modal_body_error", {}
            )

        schema = self._schema(emp)

        # 1) Listaa olemassa olevat skill-rivit tauluun
        section_rows = {}
        for sec in schema:
            if sec["key"] != "skills":
                continue
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
            section_rows[sec["key"]] = rows

        # 2) Alkuperäiset M2O-optiot VAIN skills-osion ei-riippuvaisille kentille
        initial_options = {}
        for sec in schema:
            if sec["key"] != "skills":
                continue
            sec_opts = {}
            for f in sec["fields"]:
                if f.get("type") == "many2one" and not f.get("depends_on"):
                    sec_opts[f["name"]] = self._m2o_options(emp, f, {})
            initial_options[sec["key"]] = sec_opts

        # 3) Profile-osion valmiit arvot + johdetut vuodet näyttöä varten
        profile_values = {
            "consulting_since": emp.sudo().consulting_since and emp.sudo().consulting_since.isoformat() or "",
            "strategy_since": emp.sudo().strategy_since and emp.sudo().strategy_since.isoformat() or "",
            "bio": emp.sudo().bio or "",
            "consulting_years": emp.sudo().consulting_years,
            "strategy_years": emp.sudo().strategy_years,
        }

        return request.render(
            "hr_skills_frontend.portal_skills_modal_body",
            {
                "schema": schema,
                "section_rows": section_rows,
                "initial_options": initial_options,
                "profile_values": profile_values,
                "csrf_token": request.csrf_token(),
            },
        )

    # ---- JSON: Palauta riippuvaisen many2one-kentän vaihtoehdot (skills) ----
    @http.route(
        "/my/skills_modal/m2o_options",
        type="json",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def m2o_options(self, section_key=None, field_name=None, context_values=None):
        """Käyttö JS:stä. context_values = {'skill_type_id': <id>}."""
        emp = _employee_of_current_user()
        if not emp:
            return []

        schema = self._schema(emp)
        sec = next((s for s in schema if s["key"] == section_key), None)
        if not sec:
            return []

        fdef = next(
            (
                x
                for x in sec["fields"]
                if x["name"] == field_name and x["type"] == "many2one"
            ),
            None,
        )
        if not fdef:
            return []

        return self._m2o_options(emp, fdef, context_values or {})

    def _m2o_options(self, employee, fdef, ctx_vals):
        """Palauta (id, display_name) M2O:lle."""
        Model = request.env[fdef["comodel"]].sudo()
        domain = []

        # Riippuvuuden arvo pakollinen, muuten ei mitään
        dep = fdef.get("depends_on")
        if dep:
            stid = ctx_vals.get(dep)
            if not stid:
                return []
            domain.append(("skill_type_id", "=", int(stid)))

        # Suodata pois inaktiiviset, jos mallilla on 'active'
        if "active" in Model._fields:
            domain.append(("active", "=", True))

        # Nimikentän kaunistus core-malleihin
        ctx = {}
        if fdef["comodel"] == "hr.skill":
            ctx["from_skill_dropdown"] = True
        elif fdef["comodel"] == "hr.skill.level":
            ctx["from_skill_level_dropdown"] = True

        recs = Model.with_context(**ctx).search(domain, limit=200)
        return [(r.id, r.display_name) for r in recs]

    # ---- Poistot (unlink), vain omat skill-rivit ----
    def _apply_deletions(self, employee, delete_map):
        """delete_map: {'skills': [id, id, ...]}"""
        if not delete_map or not isinstance(delete_map, dict):
            return

        schema = self._schema(employee)
        key2sec = {s["key"]: s for s in schema}

        for key, id_list in delete_map.items():
            sec = key2sec.get(key)
            if not sec or key != "skills" or not isinstance(id_list, list) or not id_list:
                continue
            try:
                Model = request.env[sec["model"]].sudo()
                recs = Model.search(
                    AND([_restrict_to_employee(employee), [("id", "in", id_list)]])
                )
                if recs:
                    recs.unlink()
            except Exception as e:
                _logger.warning(
                    "Delete failed for %s ids=%s: %s", sec and sec["model"], id_list, e
                )
                request.env.cr.rollback()

    # ---- POST: Luo uuden skill-rivin TAI päivitä profiilikentät ----
    @http.route(
        "/my/skills_modal/create",
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def create(self, **post):
        emp = _employee_of_current_user()
        if not emp:
            return request.redirect(
                (request.httprequest.referrer or "/my/home") + "?err=no_employee"
            )

        # Poistot payloadista
        delete_payload_raw = post.get("delete_payload") or ""
        try:
            delete_map = json.loads(delete_payload_raw) or {}
        except Exception as e:
            _logger.warning("Delete payload parse failed: %s", e)
            delete_map = {}

        # Aja poistot aina ensin (koskee vain skills-osiota)
        self._apply_deletions(emp, delete_map)

        # Sektion valinta
        section_key = (post.get("section_key") or "").strip()
        schema = self._schema(emp)
        sec = next((s for s in schema if s["key"] == section_key), None)
        if not sec:
            return request.redirect(request.httprequest.referrer or "/my/home")

        # --- PROFILE: kirjoita suoraan employeeen ---
        if section_key == "profile":
            allowed = {f["name"] for f in sec["fields"]}
            vals = {}
            for name in allowed:
                raw = post.get(f"profile__{name}")
                # Päivämäärät: 'YYYY-MM-DD' -> arvo tai False
                if name.endswith("_since"):
                    vals[name] = raw or False
                elif name == "bio":
                    vals[name] = raw or ""
                else:
                    vals[name] = raw
            try:
                emp.sudo().write(vals)
            except Exception as e:
                _logger.warning("Profile update failed: %s", e)
                request.env.cr.rollback()
                return request.redirect(
                    (request.httprequest.referrer or "/my/home") + "?err=profile_save"
                )
            return request.redirect(request.httprequest.referrer or "/my/home")

        # --- SKILLS: luonti kuten ennen ---
        if section_key == "skills":
            # Salli vain skeemassa sallitut kentät
            allowed = {f["name"]: f for f in sec["fields"]}
            vals = dict(sec.get("defaults", {}))

            # Lomakkeen m2o-arvot → int-id
            for name in allowed:
                raw = post.get(f"{section_key}__{name}")
                vals[name] = int(raw) if raw else False

            # Turva: pakota employee_id
            vals["employee_id"] = emp.id

            # Required-tarkistus
            for f in sec["fields"]:
                if f.get("required") and not vals.get(f["name"]):
                    return request.redirect(
                        (request.httprequest.referrer or "/my/home") + "?err=required"
                    )

            # Luo rivi
            try:
                request.env[sec["model"]].sudo().create(vals)
            except Exception as e:
                _logger.warning("Create failed for %s: %s", sec["model"], e)
                request.env.cr.rollback()
                return request.redirect(
                    (request.httprequest.referrer or "/my/home") + "?err=create"
                )

            return request.redirect(request.httprequest.referrer or "/my/home")

        # Jos sektion avain ei täsmää, paluu kotiin
        return request.redirect(request.httprequest.referrer or "/my/home")
