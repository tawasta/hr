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
    (pairs || []).forEach(([id, name]) => {
        if (!el) return;
        const opt = document.createElement("option");
        opt.value = id;
        opt.textContent = name;
        el.appendChild(opt);
    });
};

publicWidget.registry.HrEmpSkillsModal = publicWidget.Widget.extend({
    /** Root widget for the portal skills modal. */
    selector: "#oOpenHrEmpSkillsModal",

    _pendingDeletions: {},

    init() {
        this._super.apply(this, arguments);
        this.notification = this.bindService("notification");
    },

    start() {
        const modalEl = document.getElementById("hrEmpSkillsModal");
        if (modalEl) {
            modalEl.addEventListener("show.bs.modal", () => this._loadBody());
        }
        return this._super.apply(this, arguments);
    },

    async _loadBody() {
        /** Fetch fresh modal body and bind behaviors. */
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

    _afterBodyLoad() {
        /** Wire up dynamic UI after the body has been injected. */
        const root = document.getElementById("hrEmpSkillsContent");
        const formEl = document.getElementById("hrEmpSkillsForm");
        const saveBtn = document.getElementById("hrEmpSkillsSaveBtn");
        const sectionKey = document.getElementById("hrEmpSkills_section_key");
        const deleteInput = document.getElementById("hrEmpSkills_delete_payload");
        const skillsAllInput = document.getElementById(
            "hrEmpSkills_skills_all_payload"
        );
        if (!root || !formEl || !saveBtn || !sectionKey || !deleteInput) return;

        const secEl = qs(root, "#skills-section");
        const mode = (secEl && secEl.dataset ? secEl.dataset.mode : null) || "single";
        const enableSave = () => saveBtn.removeAttribute("disabled");
        const disableSaveIfNoChanges = () => {
            const hasDel = Object.values(this._pendingDeletions).some(
                (s) => s && s.size
            );
            if (
                !hasDel &&
                ["profile", "skills", "skills_all"].indexOf(sectionKey.value) === -1
            ) {
                saveBtn.setAttribute("disabled", "disabled");
            }
        };

        // Profile inputs
        qsa(root, 'input[name^="profile__"], textarea[name^="profile__"]').forEach(
            (el) => {
                const mark = () => {
                    sectionKey.value = SEC.PROFILE;
                    enableSave();
                };
                el.addEventListener("input", mark);
                el.addEventListener("change", mark);
            }
        );

        // Add button
        const addBtn = qs(root, '[data-add="skills"]');
        if (addBtn) {
            addBtn.addEventListener("click", () => {
                if (mode === "type_all") {
                    this._toggleAddBlock(root, "skills-all", true);
                    sectionKey.value = SEC.SKILLS_ALL;
                    enableSave();
                    this._wireTypeAll(root);
                } else {
                    this._toggleAddBlock(root, "skills", true);
                    sectionKey.value = SEC.SKILLS;
                    enableSave();
                    this._wireDependencies(root);
                }
            });
        }

        // Cancel buttons
        qsa(root, "[data-cancel]").forEach((btn) => {
            btn.addEventListener("click", () => {
                this._hideAllAddBlocks(root);
                if ([SEC.SKILLS, SEC.SKILLS_ALL].indexOf(sectionKey.value) !== -1) {
                    sectionKey.value = "";
                }
                disableSaveIfNoChanges();
            });
        });

        // Row deletions (delegated)
        this._initDeletionSelection(root, saveBtn, sectionKey);

        // Submit via jsonrpc
        formEl.addEventListener("submit", async (ev) => {
            ev.preventDefault();

            const delmap = {};
            Object.entries(this._pendingDeletions).forEach(([k, set]) => {
                if (set && set.size) delmap[k] = Array.from(set);
            });
            deleteInput.value = JSON.stringify(delmap);

            const key = sectionKey.value || "";
            const payload = {section_key: key, delete_map: delmap};

            // Single add
            const single = qs(root, "#addblock-skills:not(.d-none)");
            if (single && key === SEC.SKILLS) {
                if (!this._validateRequired(single)) {
                    this._alert(root, "Fill the required fields before saving.");
                    return;
                }
                payload.skills = {
                    skill_type_id:
                        (qs(single, 'select[name="skills__skill_type_id"]') || {})
                            .value || "",
                    skill_id:
                        (qs(single, 'select[name="skills__skill_id"]') || {}).value ||
                        "",
                    skill_level_id:
                        (qs(single, 'select[name="skills__skill_level_id"]') || {})
                            .value || "",
                };
            }

            // Profile
            if (key === SEC.PROFILE) {
                payload.profile = {
                    consulting_since:
                        (qs(root, 'input[name="profile__consulting_since"]') || {})
                            .value || "",
                    strategy_since:
                        (qs(root, 'input[name="profile__strategy_since"]') || {})
                            .value || "",
                    bio: (qs(root, 'textarea[name="profile__bio"]') || {}).value || "",
                };
            }

            // Type all
            const allBlock = qs(root, "#addblock-skills-all:not(.d-none)");
            if (allBlock && key === SEC.SKILLS_ALL) {
                const stid = parseInt(
                    (qs(allBlock, 'select[name="skills_all__skill_type_id"]') || {})
                        .value || "0",
                    10
                );
                const items = [];
                qsa(allBlock, "tbody tr[data-skill-id]").forEach((tr) => {
                    const sid = parseInt(tr.dataset.skillId || "0", 10);
                    const sel = qs(tr, "select");
                    const lid = parseInt((sel && sel.value) || "0", 10);
                    if (stid && sid && lid)
                        items.push({
                            skill_type_id: stid,
                            skill_id: sid,
                            skill_level_id: lid,
                        });
                });
                if (
                    !items.length &&
                    !Object.keys(delmap).length &&
                    key !== SEC.PROFILE
                ) {
                    this._alert(root, "Choose levels for at least one skill.");
                    return;
                }
                payload.skills_all_items = items;
                if (skillsAllInput) skillsAllInput.value = JSON.stringify(items);
            }

            // No changes?
            if (
                !Object.keys(delmap).length &&
                ["profile", "skills", "skills_all"].indexOf(key) === -1
            ) {
                this._alert(root, "No changes to save.");
                return;
            }

            let res = null; // ← init-declarations fix
            try {
                res = await rpc("/my/skills_modal/save", payload);
            } catch (e) {
                this._alert(root, "Saving failed. Please try again.");
                return;
            }
            if (!(res && res.ok)) {
                this._alert(root, "Saving failed. Please check required fields.");
                return;
            }

            document.getElementById("hrEmpSkillsContent").innerHTML = res.body_html;
            if (this.notification)
                this.notification.add(_t("Saved successfully"), {type: "success"});
            this._announceSuccess(
                document.getElementById("hrEmpSkillsContent"),
                _t("Changes saved.")
            );

            this._pendingDeletions = {};
            sectionKey.value = "";
            saveBtn.setAttribute("disabled", "disabled");
            this._afterBodyLoad();
        });
    },

    _announceSuccess(root, message) {
        /** Green transient success banner. */
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
        /** Checkbox delegation for deletions. */
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
        /** Track deletions and toggle Save. */
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
            tr.style.opacity = cb.checked ? "0.6" : "";
        }

        const hasAny = Object.values(this._pendingDeletions).some(
            (s) => s && s.size > 0
        );
        if (
            hasAny ||
            ["profile", "skills", "skills_all"].indexOf(sectionKeyEl.value) !== -1
        ) {
            saveBtn.removeAttribute("disabled");
        } else {
            saveBtn.setAttribute("disabled", "disabled");
        }
    },

    _toggleAddBlock(root, key, show) {
        /** Show/hide chosen add-block; ensure only one is visible. */
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
                    )
                        next.remove();
                }
            });
        });
    },

    _hideAllAddBlocks(root) {
        /** Hide all add-blocks. */
        qsa(root, "[id^='addblock-']").forEach((b) =>
            this._toggleAddBlock(root, b.id.replace("addblock-", ""), false)
        );
    },

    _wireDependencies(root) {
        /** Skill Type -> (Skill, Level) for single add. */
        const typeSel = qs(root, 'select[name="skills__skill_type_id"]');
        const skillSel = qs(root, 'select[name="skills__skill_id"]');
        const levelSel = qs(root, 'select[name="skills__skill_level_id"]');
        if (!typeSel || !skillSel || !levelSel) return;

        clearSelect(skillSel);
        clearSelect(levelSel);

        typeSel.addEventListener("change", async () => {
            clearSelect(skillSel);
            clearSelect(levelSel);
            const typeId = typeSel.value ? parseInt(typeSel.value, 10) : null;
            if (!typeId) return;
            try {
                const [skills, levels] = await Promise.all([
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
                fillSelect(skillSel, skills);
                fillSelect(levelSel, levels);
            } catch (e) {
                /* No-op */
            }
        });
    },

    _wireTypeAll(root) {
        /** Type -> render rows with level selectors. */
        const typeSel = qs(root, 'select[name="skills_all__skill_type_id"]');
        const tableBody = qs(root, "#skills-all-table-body");
        const emptyInfo = qs(root, "#skills-all-empty");
        if (!typeSel || !tableBody || !emptyInfo) return;

        const esc = (s) =>
            String(s === null || s === undefined ? "" : s) // ← no-eq-null fix
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#39;");
        const reset = (msg) => {
            tableBody.innerHTML = "";
            emptyInfo.classList.toggle("d-none", !msg);
            if (msg)
                emptyInfo.innerHTML = '<i class="fa fa-info-circle me-2"></i>' + msg;
        };

        const render = (skills, levels) => {
            reset();
            if (!skills || !skills.length) {
                reset("All skills of this type are already added to your profile.");
                return;
            }
            (skills || []).forEach(([sid, sname]) => {
                const tr = document.createElement("tr");
                tr.dataset.skillId = String(sid);
                const levelOpts = (levels || [])
                    .map(
                        ([lid, lname]) =>
                            '<option value="' + lid + '">' + esc(lname) + "</option>"
                    )
                    .join("");
                tr.innerHTML =
                    "<td>" +
                    esc(sname) +
                    '</td><td style="width:18rem"><select class="form-select form-select-sm"><option value=""></option>' +
                    levelOpts +
                    "</select></td>";
                tableBody.appendChild(tr);
            });
        };

        const load = async () => {
            reset("Select a Skill Type to see its skills.");
            const typeId = typeSel.value ? parseInt(typeSel.value, 10) : null;
            if (!typeId) return;
            try {
                const [skills, levels] = await Promise.all([
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
                render(skills || [], levels || []);
            } catch (e) {
                reset();
            }
        };

        typeSel.addEventListener("change", load);
    },

    _validateRequired(container) {
        /** Validate required selects inside container. */
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
                fb.textContent = "Required field";
                el.insertAdjacentElement("afterend", fb);
            }
        });
        const firstInvalid = qs(container, ".is-invalid");
        if (!ok && firstInvalid) firstInvalid.focus();
        return ok;
    },

    _alert(root, msg) {
        /** Show red inline alert on top. */
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
