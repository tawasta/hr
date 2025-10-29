/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.HrEmpSkillsModal = publicWidget.Widget.extend({
    selector: "#oOpenHrEmpSkillsModal",

    // Muistissa: { skills: Set([id, ...]) }
    _pendingDeletions: {},

    start() {
        this.$el.on("click", this._onOpen.bind(this));
        return this._super(...arguments);
    },

    async _onOpen() {
        const modalBody = document.getElementById("hrEmpSkillsContent");
        const formEl = document.getElementById("hrEmpSkillsForm");
        const saveBtn = document.getElementById("hrEmpSkillsSaveBtn");
        const sectionKey = document.getElementById("hrEmpSkills_section_key");
        const deleteInput = document.getElementById("hrEmpSkills_delete_payload");
        if (!modalBody || !formEl || !saveBtn || !sectionKey || !deleteInput) return;

        // Resetoi tila
        this._pendingDeletions = {};
        sectionKey.value = ""; // ei oletusta
        saveBtn.setAttribute("disabled", "disabled");

        // Lataa modal body palvelimelta
        modalBody.innerHTML = `
          <div class="d-flex align-items-center justify-content-center py-5">
            <div class="spinner-border" role="status" aria-hidden="true"></div>
            <span class="visually-hidden">Loading...</span>
          </div>`;
        try {
            const resp = await fetch("/my/skills_modal/body", {
                credentials: "same-origin",
            });
            modalBody.innerHTML = await resp.text();
        } catch {
            modalBody.innerHTML = `<div class="alert alert-danger m-3">Failed to load modal content.</div>`;
            return;
        }

        // --- Profiilikentät: aina näkyvissä. Muutos -> section_key=profile + Save enabled
        const profileInputs = modalBody.querySelectorAll('input[name^="profile__"], textarea[name^="profile__"]');
        const markProfileChanged = () => {
            sectionKey.value = "profile";
            saveBtn.removeAttribute("disabled");
        };
        profileInputs.forEach((el) => {
            el.addEventListener("input", markProfileChanged);
            el.addEventListener("change", markProfileChanged);
        });

        // --- "Add skill" -> näyttää addblockin ja kytkee riippuvuudet
        modalBody.querySelectorAll('[data-add="skills"]').forEach((btn) => {
            btn.addEventListener("click", () => {
                this._toggleAddBlock(modalBody, "skills", true);
                sectionKey.value = "skills";
                saveBtn.removeAttribute("disabled");
                this._wireDependencies(modalBody);
            });
        });

        // --- "Cancel" -> piilota skills addblock, tyhjennä section_key vain jos se on "skills"
        modalBody.querySelectorAll("[data-cancel]").forEach((btn) => {
            btn.addEventListener("click", () => {
                this._hideAllAddBlocks(modalBody);
                if (sectionKey.value === "skills") {
                    sectionKey.value = "";
                }
                const hasAnyDeletion = Object.values(this._pendingDeletions).some((s) => s && s.size);
                const hasProfileChange = profileInputs && sectionKey.value === "profile";
                if (!hasAnyDeletion && !hasProfileChange) {
                    saveBtn.setAttribute("disabled", "disabled");
                }
            });
        });

        // --- Poistocheckboxit skills-taululle
        this._initDeletionSelection(modalBody, saveBtn, sectionKey);

        // --- Submit: lisää delete_payload ja validoi tarvittaessa
        formEl.addEventListener("submit", (ev) => {
            // 1) delete_payload JSON
            const payload = {};
            Object.entries(this._pendingDeletions).forEach(([k, set]) => {
                if (set && set.size) payload[k] = Array.from(set);
            });
            deleteInput.value = JSON.stringify(payload);

            // 2) kelpoisuus
            const skillsBlock = modalBody.querySelector("#addblock-skills:not(.d-none)");
            if (skillsBlock && sectionKey.value === "skills") {
                const ok = this._validateRequired(skillsBlock);
                if (!ok) {
                    ev.preventDefault();
                    this._showAlert(modalBody, "Fill the required fields before saving.");
                    return;
                }
            }

            // Jos ei profiilimuutosta, ei skills-lisäystä eikä poistoja -> estä submit
            const hasAnyDeletion = Object.keys(payload).length > 0;
            const isProfile = sectionKey.value === "profile";
            const isSkills = sectionKey.value === "skills";
            if (!hasAnyDeletion && !isProfile && !isSkills) {
                ev.preventDefault();
                this._showAlert(modalBody, "No changes to save.");
            }
        });
    },

    // --- Poistojen hallinta ---
    _initDeletionSelection(root, saveBtn, sectionKeyEl) {
        root.querySelectorAll("[data-delcheck]").forEach((cb) => {
            cb.addEventListener("change", () => {
                const section = cb.dataset.section; // "skills"
                const id = parseInt(cb.dataset.id || "0");
                if (!section || !id) return;

                if (!this._pendingDeletions[section]) {
                    this._pendingDeletions[section] = new Set();
                }

                if (cb.checked) {
                    this._pendingDeletions[section].add(id);
                } else {
                    this._pendingDeletions[section].delete(id);
                }

                // Kevyt visuaalinen vihje poistosta
                const tr = cb.closest("tr");
                if (tr) {
                    tr.classList.toggle("table-warning", cb.checked);
                    tr.style.opacity = cb.checked ? "0.6" : "";
                }

                // Save on aktiivinen jos on poistoja TAI profiili/skills-lisäys käynnissä
                const hasAnyDeletion = Object.values(this._pendingDeletions).some(
                    (s) => s && s.size > 0
                );
                if (hasAnyDeletion || sectionKeyEl.value === "profile" || sectionKeyEl.value === "skills") {
                    saveBtn.removeAttribute("disabled");
                } else {
                    saveBtn.setAttribute("disabled", "disabled");
                }
            });
        });
    },

    // --- Addblock show/hide (vain skillsille) ---
    _toggleAddBlock(root, key, show) {
        const block = root.querySelector(`#addblock-${key}`);
        if (!block) return;

        block.classList.toggle("d-none", !show);

        // Enable vain näkyvässä
        block.querySelectorAll("input, select, textarea").forEach((el) => {
            el.disabled = !show;
            // Skills: required-merkinnät labelissa -> el.required
            const col = el.closest(".col");
            const isReq = Boolean(col && col.querySelector("label .text-danger"));
            el.required = show && isReq;
            if (!show) {
                el.classList.remove("is-invalid");
                const next = el.nextElementSibling;
                if (next && next.classList && next.classList.contains("invalid-feedback")) {
                    next.remove();
                }
            }
        });

        // Piilota muut addblockit (varmuuden vuoksi, vaikka meillä on vain skills)
        root.querySelectorAll("[id^='addblock-']").forEach((other) => {
            if (other === block) return;
            other.classList.add("d-none");
            other.querySelectorAll("input, select, textarea").forEach((el) => {
                el.disabled = true;
                el.required = false;
                el.classList.remove("is-invalid");
                const next = el.nextElementSibling;
                if (next && next.classList && next.classList.contains("invalid-feedback")) {
                    next.remove();
                }
            });
        });
    },

    _hideAllAddBlocks(root) {
        root.querySelectorAll("[id^='addblock-']").forEach((b) =>
            this._toggleAddBlock(root, b.id.replace("addblock-", ""), false)
        );
    },

    // --- Riippuvuudet: Skill Type -> (Skill, Level) ---
    _wireDependencies(root) {
        const typeSel = root.querySelector('select[name="skills__skill_type_id"]');
        const skillSel = root.querySelector('select[name="skills__skill_id"]');
        const levelSel = root.querySelector('select[name="skills__skill_level_id"]');
        if (!typeSel || !skillSel || !levelSel) return;

        const reset = (el) => {
            el.innerHTML = "<option value=''></option>";
        };

        // Aluksi tyhjät listat child-kentille
        reset(skillSel);
        reset(levelSel);

        typeSel.addEventListener("change", async () => {
            reset(skillSel);
            reset(levelSel);

            const typeId = typeSel.value ? parseInt(typeSel.value, 10) : null;
            if (!typeId) return;

            const ctx = { skill_type_id: typeId };
            try {
                const [skills, levels] = await Promise.all([
                    jsonrpc("/my/skills_modal/m2o_options", {
                        section_key: "skills",
                        field_name: "skill_id",
                        context_values: ctx,
                    }),
                    jsonrpc("/my/skills_modal/m2o_options", {
                        section_key: "skills",
                        field_name: "skill_level_id",
                        context_values: ctx,
                    }),
                ]);

                (skills || []).forEach(([id, name]) => {
                    const o = document.createElement("option");
                    o.value = id;
                    o.textContent = name;
                    skillSel.appendChild(o);
                });

                (levels || []).forEach(([id, name]) => {
                    const o = document.createElement("option");
                    o.value = id;
                    o.textContent = name;
                    levelSel.appendChild(o);
                });
            } catch {
                // Jätetään tyhjäksi virhetilanteessa
            }
        });
    },

    // --- Kevyt required-validointi näkyvässä skills-addblockissa ---
    _validateRequired(container) {
        let ok = true;

        container.querySelectorAll(".is-invalid").forEach((el) => el.classList.remove("is-invalid"));
        container.querySelectorAll(".invalid-feedback").forEach((el) => el.remove());

        container.querySelectorAll("select").forEach((el) => {
            if (el.disabled || !el.required) return;
            const val = (el.value || "").trim();
            if (!val) {
                ok = false;
                el.classList.add("is-invalid");
                const fb = document.createElement("div");
                fb.className = "invalid-feedback";
                fb.textContent = "Required field";
                el.insertAdjacentElement("afterend", fb);
            }
        });

        if (!ok) {
            const first = container.querySelector(".is-invalid");
            if (first) first.focus();
        }
        return ok;
    },

    _showAlert(root, msg) {
        root.querySelectorAll(".portal-schema-alert").forEach((a) => a.remove());
        const el = document.createElement("div");
        el.className = "alert alert-danger portal-schema-alert";
        el.setAttribute("role", "alert");
        el.innerHTML = `<i class="fa fa-exclamation-triangle me-2"></i>${msg}`;
        root.prepend(el);
    },
});
