# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.osv.expression import AND
import json
import logging

_logger = logging.getLogger(__name__)


# ---------- Apufunktiot ----------

def _employee_of_current_user():
    """Palauta kirjautuneen käyttäjän työntekijä (hr.employee) tai False.
    - Käyttää user.employee_id:tä
    - Fallback: etsi user_id:llä
    """
    user = request.env.user.sudo()
    emp = user.employee_id
    if not emp:
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
    return emp


def _restrict_to_employee(emp):
    """Domain, joka rajaa hakua vain tiettyyn työntekijään."""
    return [('employee_id', '=', emp.id)]


# ---------- Kontrolleri ----------

class PortalSkillProfileController(http.Controller):
    """
    Portal: "My skills" -modaali
      - Listaa nykyisen työntekijän hr.employee.skill -rivit
      - Filtroi riippuvat M2O-kentät (skill_type -> skills & levels)
      - Tekee luonnin ja poiston samassa lomakkeessa
    """

    # ---- SKEEMA: kuvaa modaalin osiot, listan kolumnit ja input-kentät ----
    def _schema(self, employee):
        return [{
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
        }]

    # ---- GET: Rakenna modal-body (lista + initial options) ----
    @http.route(
        "/my/skills_modal/body",
        type="http", auth="user", website=True, methods=["GET"]
    )
    def skills_modal_body(self, **kw):
        emp = _employee_of_current_user()
        if not emp:
            return request.render("hr_skills_frontend.portal_skills_modal_body_error", {})

        schema = self._schema(emp)

        # 1) Listaa olemassa olevat rivit (näytetään taulussa)
        section_rows = {}
        for sec in schema:
            Model = request.env[sec["model"]].sudo()
            recs = Model.search(_restrict_to_employee(emp), order="id desc", limit=200)
            rows = []
            for r in recs:
                row = {"id": r.id}
                for col in sec["list_columns"]:
                    val = getattr(r, col["name"])
                    row[col["name"]] = (val.display_name if col.get("type") == "m2o" else val) or ""
                rows.append(row)
            section_rows[sec["key"]] = rows

        # 2) Alkuperäiset M2O-optiot VAIN ei-riippuvaisille kentille (type)
        initial_options = {}
        for sec in schema:
            sec_opts = {}
            for f in sec["fields"]:
                if f["type"] == "many2one" and not f.get("depends_on"):
                    sec_opts[f["name"]] = self._m2o_options(emp, f, {})
            initial_options[sec["key"]] = sec_opts

        return request.render(
            "hr_skills_frontend.portal_skills_modal_body",
            {
                "schema": schema,
                "section_rows": section_rows,
                "initial_options": initial_options,
                "csrf_token": request.csrf_token(),
            },
        )

    # ---- JSON: Palauta riippuvaisen many2one-kentän vaihtoehdot ----
    @http.route(
        "/my/skills_modal/m2o_options",
        type="json", auth="user", website=True, methods=["POST"]
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
            (x for x in sec["fields"] if x["name"] == field_name and x["type"] == "many2one"),
            None
        )
        if not fdef:
            return []

        return self._m2o_options(emp, fdef, context_values or {})

    def _m2o_options(self, employee, fdef, ctx_vals):
        """Palauta (id, display_name) M2O:lle. Suodatus tehdään suoraan Pythonissa.
        - Jos kentällä on depends_on=skill_type_id ja arvo puuttuu → []
        - Muutoin domain [('skill_type_id', '=', <ctx arvo>)] + ('active','=',True) jos kenttä on
        - Kontekstiliput: hr.skill → from_skill_dropdown, hr.skill.level → from_skill_level_dropdown
        """
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

    # ---- Poistot (unlink), vain omat rivit ----
    def _apply_deletions(self, employee, delete_map):
        """delete_map: {'skills': [id, id, ...]}"""
        if not delete_map or not isinstance(delete_map, dict):
            return

        schema = self._schema(employee)
        key2sec = {s["key"]: s for s in schema}

        for key, id_list in delete_map.items():
            sec = key2sec.get(key)
            if not sec or not isinstance(id_list, list) or not id_list:
                continue
            try:
                Model = request.env[sec["model"]].sudo()
                recs = Model.search(AND([_restrict_to_employee(employee), [("id", "in", id_list)]]))
                if recs:
                    recs.unlink()
            except Exception as e:
                _logger.warning("Delete failed for %s ids=%s: %s", sec and sec["model"], id_list, e)
                request.env.cr.rollback()

    # ---- POST: Luo uuden ja/tai poista valitut ----
    @http.route(
        "/my/skills_modal/create",
        type="http", auth="user", website=True, methods=["POST"]
    )
    def create(self, **post):
        emp = _employee_of_current_user()
        if not emp:
            return request.redirect((request.httprequest.referrer or "/my/home") + "?err=no_employee")

        # Poistot payloadista
        delete_payload_raw = post.get("delete_payload") or ""
        try:
            delete_map = json.loads(delete_payload_raw) or {}
        except Exception as e:
            _logger.warning("Delete payload parse failed: %s", e)
            delete_map = {}

        # Aja poistot aina ensin
        self._apply_deletions(emp, delete_map)

        # Luonti vain jos section_key=skills
        section_key = (post.get("section_key") or "").strip()
        schema = self._schema(emp)
        sec = next((s for s in schema if s["key"] == section_key), None)
        if not sec:
            return request.redirect(request.httprequest.referrer or "/my/home")

        # Salli vain skeemassa sallitut kentät
        allowed = {f["name"]: f for f in sec["fields"]}
        vals = dict(sec.get("defaults", {}))

        # Lomakkeen m2o-arvot → int-id
        for name in allowed:
            raw = post.get(f"{section_key}__{name}")
            vals[name] = int(raw) if raw else False

        # Turva: pakota employee_id (vaikka joku yrittäisi peukaloida lomakkeen)
        vals["employee_id"] = emp.id

        # Required-tarkistus
        for f in sec["fields"]:
            if f.get("required") and not vals.get(f["name"]):
                return request.redirect((request.httprequest.referrer or "/my/home") + "?err=required")

        # Luo rivi
        try:
            request.env[sec["model"]].sudo().create(vals)
        except Exception as e:
            _logger.warning("Create failed for %s: %s", sec["model"], e)
            request.env.cr.rollback()
            return request.redirect((request.httprequest.referrer or "/my/home") + "?err=create")

        return request.redirect(request.httprequest.referrer or "/my/home")
