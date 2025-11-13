/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import {jsonrpc} from "@web/core/network/rpc_service";
import {_t} from "@web/core/l10n/translation";

const SEC = {PROFILE: "profile", SKILLS: "skills", SKILLS_ALL: "skills_all"};
const rpc = (route, params) => jsonrpc(route, params);

// DOM helpers
const qs = (r, s) => (r || document).querySelector(s);
const qsa = (r, s) => Array.from((r || document).querySelectorAll(s));
const clearSelect = (el) => {
    if (el) el.innerHTML = "<option value=''></option>";
};
const fillSelect = (el, pairs) => {
    (pairs || []).forEach(function (pair) {
        if (!el) return;
        const id = pair[0],
            name = pair[1];
        const opt = document.createElement("option");
        opt.value = id;
        opt.textContent = name;
        el.appendChild(opt);
    });
};

publicWidget.registry.HrEmpSkillsModal = publicWidget.Widget.extend({
    selector: "#oOpenHrEmpSkillsModal",

    // Internal state
    _pendingDeletions: {},
    _saving: false,
    _submitCtl: null,

    init() {
        this._super.apply(this, arguments);
        this.notification = this.bindService("notification");
        this._onSubmit = this._onSubmit.bind(this);
    },

    start() {
        const modalEl = document.getElementById("hrEmpSkillsModal");
        if (modalEl) {
            modalEl.addEventListener("show.bs.modal", () => this._loadBody());
        }
        this._bindSubmit(); // Bind once
        return this._super.apply(this, arguments);
    },

    destroy() {
        try {
            if (this._submitCtl && typeof this._submitCtl.abort === "function") {
                this._submitCtl.abort();
            }
        } catch (e) {
            /* No-op */
        }
        return this._super.apply(this, arguments);
    },

    _bindSubmit() {
        const formEl = document.getElementById("hrEmpSkillsForm");
        if (!formEl) return;
        try {
            if (this._submitCtl && typeof this._submitCtl.abort === "function") {
                this._submitCtl.abort();
            }
        } catch (e) {}
        this._submitCtl = new AbortController();
        formEl.addEventListener("submit", this._onSubmit, {
            signal: this._submitCtl.signal,
        });
    },

    async _loadBody() {
        const modalBody = document.getElementById("hrEmpSkillsContent");
        const formEl = document.getElementById("hrEmpSkillsForm");
        if (!modalBody || !formEl) return;

        this._pendingDeletions = {};
        modalBody.innerHTML =
            '<div class="d-flex align-items-center justify-content-center py-5">' +
            '<div class="spinner-border" role="status" aria-hidden="true"></div>' +
            '<span class="visually-hidden">Loading...</span>' +
            "</div>";

        try {
            const resp = await fetch("/my/skills_modal/body", {
                credentials: "same-origin",
            });
            modalBody.innerHTML = await resp.text();
        } catch (e) {
            modalBody.innerHTML =
                '<div class="alert alert-danger m-3">Failed to load modal content.</div>';
            return;
        }
        this._afterBodyLoad();
    },

    // ---- generic helpers ----------------------------------------------------

    _markDirty(section) {
        // Central place to mark “there are unsaved changes” and enable Save.
        const saveBtn = document.getElementById("hrEmpSkillsSaveBtn");
        const sectionKey = document.getElementById("hrEmpSkills_section_key");
        if (sectionKey) sectionKey.value = section || "";
        if (saveBtn) saveBtn.removeAttribute("disabled");
    },

    _afterBodyLoad() {
        const root = document.getElementById("hrEmpSkillsContent");
        const saveBtn = document.getElementById("hrEmpSkillsSaveBtn");
        const sectionKey = document.getElementById("hrEmpSkills_section_key");
        const deleteInput = document.getElementById("hrEmpSkills_delete_payload");
        if (!root || !saveBtn || !sectionKey || !deleteInput) return;

        // Mode
        const secEl = qs(root, "#skills-section");
        const mode = (secEl && secEl.dataset ? secEl.dataset.mode : null) || "single";

        // Profile fields -> mark dirty on any change
        qsa(root, 'input[name^="profile__"], textarea[name^="profile__"]').forEach(
            (el) => {
                const mark = () => this._markDirty(SEC.PROFILE);
                el.addEventListener("input", mark);
                el.addEventListener("change", mark);
            }
        );

        // Add button (single vs type_all)
        const addBtn = qs(root, '[data-add="skills"]');
        if (addBtn) {
            addBtn.addEventListener("click", () => {
                if (mode === "type_all") {
                    this._toggleAddBlock(root, "skills-all", true);
                    this._markDirty(SEC.SKILLS_ALL);
                    this._wireTypeAll(root);
                } else {
                    this._toggleAddBlock(root, "skills", true);
                    this._markDirty(SEC.SKILLS);
                    this._wireDependencies(root);
                }
            });
        }

        // Cancel buttons
        qsa(root, "[data-cancel]").forEach((btn) => {
            btn.addEventListener("click", () => {
                this._hideAllAddBlocks(root);
                if (
                    sectionKey &&
                    (sectionKey.value === SEC.SKILLS ||
                        sectionKey.value === SEC.SKILLS_ALL)
                ) {
                    sectionKey.value = "";
                }
                // Disable save if nothing else pending
                const hasDel = Object.values(this._pendingDeletions).some(
                    (s) => s && s.size
                );
                if (!hasDel && saveBtn) saveBtn.setAttribute("disabled", "disabled");
            });
        });

        // Deletion delegation
        this._initDeletionSelection(root, saveBtn, sectionKey);
    },

    async _onSubmit(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        if (this._saving) return;

        const root = document.getElementById("hrEmpSkillsContent");
        const saveBtn = document.getElementById("hrEmpSkillsSaveBtn");
        const sectionKey = document.getElementById("hrEmpSkills_section_key");
        const deleteInput = document.getElementById("hrEmpSkills_delete_payload");
        const skillsAllInput = document.getElementById(
            "hrEmpSkills_skills_all_payload"
        );
        if (!root || !saveBtn || !sectionKey || !deleteInput) return;

        this._saving = true;
        saveBtn.setAttribute("disabled", "disabled");

        const alertAndUnlock = (msg) => {
            this._alert(root, msg);
            this._saving = false;
        };

        try {
            // Deletions
            const delmap = {};
            Object.entries(this._pendingDeletions).forEach(function ([k, set]) {
                if (set && set.size) delmap[k] = Array.from(set);
            });
            deleteInput.value = JSON.stringify(delmap);

            const key = (sectionKey.value || "").trim();
            const payload = {section_key: key, delete_map: delmap};

            // Single add
            const single = qs(root, "#addblock-skills:not(.d-none)");
            if (single && key === SEC.SKILLS) {
                if (!this._validateRequired(single)) {
                    return alertAndUnlock(
                        _t("Fill the required fields before saving.")
                    );
                }
                const typeEl = qs(single, 'select[name="skills__skill_type_id"]');
                const skillEl = qs(single, 'select[name="skills__skill_id"]');
                const levelEl = qs(single, 'select[name="skills__skill_level_id"]');
                payload.skills = {
                    skill_type_id: typeEl && typeEl.value ? typeEl.value : "",
                    skill_id: skillEl && skillEl.value ? skillEl.value : "",
                    skill_level_id: levelEl && levelEl.value ? levelEl.value : "",
                };
            }

            // Profile
            if (key === SEC.PROFILE) {
                const cEl = qs(root, 'input[name="profile__consulting_since"]');
                const sEl = qs(root, 'input[name="profile__strategy_since"]');
                const bEl = qs(root, 'textarea[name="profile__bio"]');
                payload.profile = {
                    consulting_since: cEl ? cEl.value || "" : "",
                    strategy_since: sEl ? sEl.value || "" : "",
                    bio: bEl ? bEl.value || "" : "",
                };
            }

            // Type-all
            const allBlock = qs(root, "#addblock-skills-all:not(.d-none)");
            if (allBlock && key === SEC.SKILLS_ALL) {
                const typeSel = qs(
                    allBlock,
                    'select[name="skills_all__skill_type_id"]'
                );
                const stid = parseInt(
                    typeSel && typeSel.value ? typeSel.value : "0",
                    10
                );
                const items = [];
                qsa(allBlock, "tbody tr[data-skill-id]").forEach(function (tr) {
                    const sid = parseInt(tr.dataset.skillId || "0", 10);
                    const sel = qs(tr, "select");
                    const lid = parseInt(sel && sel.value ? sel.value : "0", 10);
                    if (stid && sid && lid) {
                        items.push({
                            skill_type_id: stid,
                            skill_id: sid,
                            skill_level_id: lid,
                        });
                    }
                });
                if (
                    !items.length &&
                    !Object.keys(delmap).length &&
                    key !== SEC.PROFILE
                ) {
                    return alertAndUnlock(_t("Choose levels for at least one skill."));
                }
                payload.skills_all_items = items;
                if (skillsAllInput) skillsAllInput.value = JSON.stringify(items);
            }

            // No-op?
            if (
                !Object.keys(delmap).length &&
                key !== SEC.PROFILE &&
                key !== SEC.SKILLS &&
                key !== SEC.SKILLS_ALL
            ) {
                return alertAndUnlock(_t("No changes to save."));
            }

            const res = await rpc("/my/skills_modal/save", payload);
            if (!res || !res.ok) {
                return alertAndUnlock(
                    _t("Saving failed. Please check required fields.")
                );
            }

            // Refresh body & rewire
            const contentEl = document.getElementById("hrEmpSkillsContent");
            if (contentEl) contentEl.innerHTML = res.body_html;
            if (this.notification)
                this.notification.add(_t("Saved successfully"), {type: "success"});
            this._announceSuccess(
                document.getElementById("hrEmpSkillsContent"),
                _t("Changes saved.")
            );
            this._pendingDeletions = {};
            sectionKey.value = "";
            this._afterBodyLoad();
        } catch (e) {
            alertAndUnlock(_t("Saving failed. Please try again."));
        } finally {
            const btn = document.getElementById("hrEmpSkillsSaveBtn");
            if (btn) btn.setAttribute("disabled", "disabled");
            this._saving = false;
        }
    },

    _announceSuccess(root, message) {
        if (!root) return;
        qsa(root, ".portal-schema-success").forEach((a) => a.remove());
        const el = document.createElement("div");
        el.className = "alert alert-success portal-schema-success";
        el.setAttribute("role", "status");
        el.innerHTML = '<i class="fa fa-check-circle me-2"></i>' + message;
        root.prepend(el);
        const scroller = qs(root, ".modal-body") || root;
        scroller.scrollTo({top: 0, behavior: "smooth"});
        setTimeout(() => {
            el.classList.add("fade");
            setTimeout(() => el.remove(), 300);
        }, 3000);
    },

    _initDeletionSelection(root, saveBtn, sectionKeyEl) {
        const body = qs(root, "#skills-table-body");
        const onChange = (cb) => this._onDelChange(cb, saveBtn, sectionKeyEl);
        if (!body) {
            qsa(root, "[data-delcheck]").forEach((cb) =>
                cb.addEventListener("change", () => onChange(cb))
            );
            return;
        }
        body.addEventListener("change", (ev) => {
            const t = ev.target;
            if (t && t.matches && t.matches("[data-delcheck]")) onChange(t);
        });
    },

    _onDelChange(cb, saveBtn, sectionKeyEl) {
        const section = cb.dataset.section;
        const id = parseInt(cb.dataset.id || "0", 10);
        if (!section || !id) return;

        if (!this._pendingDeletions[section])
            this._pendingDeletions[section] = new Set();
        if (cb.checked) this._pendingDeletions[section].add(id);
        else this._pendingDeletions[section].delete(id);

        const tr = cb.closest("tr");
        if (tr) {
            tr.classList.toggle("table-warning", cb.checked);
        }

        const hasAny = Object.values(this._pendingDeletions).some(
            (s) => s && s.size > 0
        );
        if (
            hasAny ||
            (sectionKeyEl &&
                (sectionKeyEl.value === SEC.PROFILE ||
                    sectionKeyEl.value === SEC.SKILLS ||
                    sectionKeyEl.value === SEC.SKILLS_ALL))
        ) {
            if (saveBtn) saveBtn.removeAttribute("disabled");
        } else if (saveBtn) saveBtn.setAttribute("disabled", "disabled");
    },

    _toggleAddBlock(root, key, show) {
        const target = qs(root, "#addblock-" + key);
        if (!target) return;
        qsa(root, "[id^='addblock-']").forEach((blk) => {
            const on = blk === target && show;
            blk.classList.toggle("d-none", !on);
            qsa(blk, "input, select, textarea").forEach((el) => {
                el.disabled = !on;
                const col = el.closest(".col");
                const req = Boolean(col && qs(col, "label .text-danger"));
                el.required = on && req;
                if (!on) {
                    el.classList.remove("is-invalid");
                    const next = el.nextElementSibling;
                    if (
                        next &&
                        next.classList &&
                        next.classList.contains("invalid-feedback")
                    ) {
                        next.remove();
                    }
                }
            });
        });
    },

    _hideAllAddBlocks(root) {
        qsa(root, "[id^='addblock-']").forEach((b) =>
            this._toggleAddBlock(root, b.id.replace("addblock-", ""), false)
        );
    },

    _wireDependencies(root) {
        // Single add dependencies
        const typeSel = qs(root, 'select[name="skills__skill_type_id"]');
        const skillSel = qs(root, 'select[name="skills__skill_id"]');
        const levelSel = qs(root, 'select[name="skills__skill_level_id"]');
        if (!typeSel || !skillSel || !levelSel) return;

        clearSelect(skillSel);
        clearSelect(levelSel);

        // Any change in these selects marks dirty
        [typeSel, skillSel, levelSel].forEach((el) => {
            el.addEventListener("change", () => this._markDirty(SEC.SKILLS));
        });

        typeSel.addEventListener("change", async () => {
            clearSelect(skillSel);
            clearSelect(levelSel);
            const typeId = typeSel.value ? parseInt(typeSel.value, 10) : null;
            if (!typeId) return;
            try {
                const results = await Promise.all([
                    rpc("/my/skills_modal/m2o_options", {
                        section_key: SEC.SKILLS,
                        field_name: "skill_id",
                        context_values: {skill_type_id: typeId, exclude_existing: true},
                    }),
                    rpc("/my/skills_modal/m2o_options", {
                        section_key: SEC.SKILLS,
                        field_name: "skill_level_id",
                        context_values: {skill_type_id: typeId},
                    }),
                ]);
                const skills = results[0],
                    levels = results[1];
                fillSelect(skillSel, skills);
                fillSelect(levelSel, levels);
            } catch (e) {}
        });
    },

    _wireTypeAll(root) {
        // Type-all block
        const typeSel = qs(root, 'select[name="skills_all__skill_type_id"]');
        const tableBody = qs(root, "#skills-all-table-body");
        const emptyInfo = qs(root, "#skills-all-empty");
        if (!typeSel || !tableBody || !emptyInfo) return;

        const esc = (s) => {
            const v = s === null || s === undefined ? "" : String(s);
            return v
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#39;");
        };

        const reset = (msg) => {
            tableBody.innerHTML = "";
            emptyInfo.classList.toggle("d-none", !msg);
            if (msg)
                emptyInfo.innerHTML = '<i class="fa fa-info-circle me-2"></i>' + msg;
        };

        const render = (skills, levels) => {
            reset();
            if (!skills || !skills.length) {
                reset(_t("All skills of this type are already added to your profile."));
                return;
            }
            (skills || []).forEach(function (pair) {
                const sid = pair[0],
                    sname = pair[1];
                const tr = document.createElement("tr");
                tr.dataset.skillId = String(sid);
                const levelOpts = (levels || [])
                    .map(function (lv) {
                        return (
                            '<option value="' + lv[0] + '">' + esc(lv[1]) + "</option>"
                        );
                    })
                    .join("");
                tr.innerHTML =
                    "<td>" +
                    esc(sname) +
                    "</td>" +
                    '<td style="width:18rem">' +
                    '<select class="form-select form-select-sm">' +
                    '<option value=""></option>' +
                    levelOpts +
                    "</select></td>";
                tableBody.appendChild(tr);
            });

            // Any level change -> mark dirty so Save enables
            qsa(tableBody, "select").forEach((sel) => {
                sel.addEventListener("change", () => this._markDirty(SEC.SKILLS_ALL));
            });
        };

        const load = async () => {
            reset(_t("Select a Skill Type to see its skills."));
            const typeId = typeSel.value ? parseInt(typeSel.value, 10) : null;
            if (!typeId) return;
            try {
                const results = await Promise.all([
                    rpc("/my/skills_modal/m2o_options", {
                        section_key: SEC.SKILLS,
                        field_name: "skill_id",
                        context_values: {skill_type_id: typeId, exclude_existing: true},
                    }),
                    rpc("/my/skills_modal/m2o_options", {
                        section_key: SEC.SKILLS,
                        field_name: "skill_level_id",
                        context_values: {skill_type_id: typeId},
                    }),
                ]);
                const skills = results[0],
                    levels = results[1];
                render(skills || [], levels || []);
            } catch (e) {
                reset();
            }
        };

        // Type change both loads rows and marks dirty
        typeSel.addEventListener("change", () => {
            this._markDirty(SEC.SKILLS_ALL);
            load();
        });
    },

    _validateRequired(container) {
        let ok = true;
        qsa(container, ".is-invalid").forEach((el) =>
            el.classList.remove("is-invalid")
        );
        qsa(container, ".invalid-feedback").forEach((el) => el.remove());
        qsa(container, "select").forEach((el) => {
            if (el.disabled || !el.required) return;
            if (!(el.value || "").trim()) {
                ok = false;
                el.classList.add("is-invalid");
                const fb = document.createElement("div");
                fb.className = "invalid-feedback";
                fb.textContent = _t("Required field");
                el.insertAdjacentElement("afterend", fb);
            }
        });
        const first = qs(container, ".is-invalid");
        if (first) first.focus();
        return ok;
    },

    _alert(root, msg) {
        qsa(root, ".portal-schema-alert").forEach((a) => a.remove());
        const el = document.createElement("div");
        el.className = "alert alert-danger portal-schema-alert";
        el.setAttribute("role", "alert");
        el.innerHTML = '<i class="fa fa-exclamation-triangle me-2"></i>' + msg;
        root.prepend(el);
        const scroller = root.closest(".modal-body") || root;
        scroller.scrollTo({top: 0, behavior: "smooth"});
    },
});
