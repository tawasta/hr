/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.PortalExpenseModalMulti = publicWidget.Widget.extend({
    selector: ".o_portal_wrap",

    start() {
        this._super(...arguments);

        this.$modal = $("#portalCreateExpenseModal");
        if (!this.$modal.length) return this._super(...arguments);
        this.$ssnInput = this.$modal.find("#partner_ssn_input");
        this.$ssnError = this.$modal.find("#partner_ssn_error");

        this.$country = this.$modal.find("#partner_country_id");
        this.$state = this.$modal.find("#partner_state_id");

        this.$modal.on("shown.bs.modal", () => {
            const $wrap = this.$modal.find(".js-expense-lines-cards");
            if ($wrap.length && !$wrap.find(".js-expense-line-card").length) {
                this._addLine(true);
            }
            this._initTempusInside(this.$modal);
            this._updateLineNumbers();
            this._filterStatesByCountry();
        });

        this.$modal.on("click", ".js-add-expense-line", (ev) => {
            ev.preventDefault();
            this._addLine(true);
        });

        this.$modal.on("change", "#partner_country_id", () => {
            this._filterStatesByCountry(true);
        });

        this.$modal.on("click", ".js-remove-expense-line", (ev) => {
            ev.preventDefault();
            const $card = $(ev.currentTarget).closest(".js-expense-line-card");
            $card.remove();

            const $wrap = this.$modal.find(".js-expense-lines-cards");
            if ($wrap.find(".js-expense-line-card").length === 0) {
                this._addLine(true);
            } else {
                this._updateLineNumbers();
            }
        });

        this.$modal.on(
            "input change",
            ".js-expense-line-card input, .js-expense-line-card select",
            (ev) => {
                const $card = $(ev.currentTarget).closest(".js-expense-line-card");
                this._updateCardHeader($card);
            }
        );

        // Live HETU validation
        this.$modal.on("input blur", "#partner_ssn_input", (ev) => {
            this._validateHetu($(ev.currentTarget).val());
        });

        // Block submit if HETU invalid (empty allowed)
        this.$modal.on("submit", "form[action='/my/expenses/create']", (ev) => {
            const ok = this._validateHetu(
                this.$ssnInput && this.$ssnInput.length ? this.$ssnInput.val() : ""
            );
            if (!ok) {
                ev.preventDefault();
                ev.stopPropagation();
                if (this.$ssnInput && this.$ssnInput.length)
                    this.$ssnInput.trigger("focus");
            }
        });

        return this._super(...arguments);
    },

    _nextIndex() {
        const $wrap = this.$modal.find(".js-expense-lines-cards");
        const current = parseInt($wrap.attr("data-next-index") || "1", 10);
        $wrap.attr("data-next-index", String(current + 1));
        return current;
    },

    _filterStatesByCountry(resetSelection) {
        if (
            !this.$country ||
            !this.$country.length ||
            !this.$state ||
            !this.$state.length
        ) {
            return;
        }

        const countryId = (this.$country.val() || "").toString();
        const $options = this.$state.find("option");

        // Keep the placeholder always visible
        $options.each(function () {
            const $opt = $(this);
            const val = ($opt.attr("value") || "").toString();

            if (!val) {
                $opt.prop("disabled", false).prop("hidden", false).show();
                return;
            }

            const optCountry = ($opt.data("country-id") || "").toString();

            if (!countryId) {
                // No country selected => hide all states (except placeholder)
                $opt.prop("hidden", true).hide();
                return;
            }

            const match = optCountry === countryId;
            $opt.prop("hidden", !match);
            if (match) $opt.show();
            else $opt.hide();
        });

        // If current selected state doesn't belong to selected country -> reset
        const selectedVal = (this.$state.val() || "").toString();
        if (selectedVal) {
            const $selected = this.$state.find(`option[value="${selectedVal}"]`);
            const selectedCountry = ($selected.data("country-id") || "").toString();
            if (countryId && selectedCountry !== countryId) {
                this.$state.val("");
            }
        }

        if (resetSelection) {
            this.$state.val("");
        }

        // If there are no states for this country, keep placeholder and disable select
        const hasAny =
            this.$state.find("option").filter(function () {
                const val = ($(this).attr("value") || "").toString();
                if (!val) return false;
                return !$(this).prop("hidden");
            }).length > 0;

        this.$state.prop("disabled", countryId ? !hasAny : true);
    },

    _addLine(open) {
        const $wrap = this.$modal.find(".js-expense-lines-cards");
        if (!$wrap.length) return;

        const idx = this._nextIndex();

        const $tmpl = this.$modal.find("template#portal_expense_line_tpl");
        if (!$tmpl.length) {
            console.error("Template #portal_expense_line_tpl not found");
            return;
        }

        const html = $tmpl.html().replaceAll("__IDX__", String(idx));
        const $node = $(html);
        $wrap.append($node);

        this._initTempusInside($node);
        this._updateLineNumbers();
        this._updateCardHeader($node);

        if (open) {
            // After replaceAll("__IDX__", idx): id becomes portalExpLineBody_1 (NOT ...___1__)
            const collapseId = `portalExpLineBody_${idx}`;
            const $collapse = $node.find(`#${collapseId}`);
            const $btn = $node.find(`[data-bs-target="#${collapseId}"]`);

            if ($collapse.length) $collapse.addClass("show");
            if ($btn.length)
                $btn.removeClass("collapsed").attr("aria-expanded", "true");
        }
    },

    _updateLineNumbers() {
        const $cards = this.$modal.find(".js-expense-line-card");
        $cards.each(function (i) {
            $(this)
                .find(".js-line-no")
                .text(String(i + 1));
        });
    },

    _updateCardHeader($card) {
        const idx = $card.attr("data-idx");

        const name = ($card.find(`[name="line_name_${idx}"]`).val() || "")
            .toString()
            .trim();
        const qty = ($card.find(`[name="line_quantity_${idx}"]`).val() || "")
            .toString()
            .trim();
        const unit = ($card.find(`[name="line_price_unit_${idx}"]`).val() || "")
            .toString()
            .trim();

        const currency = (
            $card
                .find(`[name="line_price_unit_${idx}"]`)
                .closest(".input-group")
                .find(".input-group-text")
                .text() || ""
        ).trim();

        let summary = name || "";

        if (qty && unit) {
            summary += `${summary ? " · " : ""}${qty} × ${unit}${
                currency ? " " + currency : ""
            }`;
        }

        $card.find(".js-line-summary").text(summary);
    },

    _initTempusInside($root) {
        if (!$root || !$root.length) return;

        $root.find("input.datetimepicker-input").each(function () {
            const el = this;
            if (el.dataset.tdInitialized === "1") return;
            el.dataset.tdInitialized = "1";

            if (typeof tempusDominus === "undefined") {
                console.error("Tempus Dominus is not loaded.");
                return;
            }

            // eslint-disable-next-line no-undef
            const instance = new tempusDominus.TempusDominus(el, {
                display: {
                    components: {
                        calendar: true,
                        date: true,
                        month: true,
                        year: true,
                        decades: true,
                        clock: false,
                    },
                    buttons: {today: true, clear: true, close: true},
                    icons: {
                        time: "fa fa-clock",
                        date: "fa fa-calendar",
                        up: "fa fa-arrow-up",
                        down: "fa fa-arrow-down",
                        previous: "fa fa-chevron-left",
                        next: "fa fa-chevron-right",
                        today: "fa fa-calendar-check",
                        clear: "fa fa-trash",
                        close: "fa fa-times",
                    },
                    viewMode: "calendar",
                    toolbarPlacement: "bottom",
                    calendarWeeks: true,
                },
                localization: {format: "dd.MM.yyyy"},
            });

            const $group = $(el).closest(".input-group");
            const $btn = $group.find(".input-group-text").first();
            if ($btn && $btn.length) {
                $btn.off("click.portalExpenseTempus").on(
                    "click.portalExpenseTempus",
                    () => {
                        try {
                            instance.show();
                        } catch (e) {
                            el.focus();
                        }
                    }
                );
            }
        });
    },

    _validateHetu(value) {
        // If your XML doesn't include the field for some reason, don't block anything
        if (!this.$ssnInput || !this.$ssnInput.length) return true;

        const raw = (value !== undefined && value !== null ? value : "")
            .toString()
            .trim();

        // Empty is allowed (matches backend: validate only if provided)
        if (!raw) {
            this.$ssnInput.removeClass("is-invalid");
            if (this.$ssnError && this.$ssnError.length) this.$ssnError.hide().text("");
            return true;
        }

        const s = raw.toUpperCase();
        const m = s.match(/^(\d{2})(0[1-9]|1[0-2])(\d{2})([-+A])(\d{3})([0-9A-Y])$/);

        let ok = false;
        if (m) {
            const dd = m[1];
            const mm = m[2];
            const yy = m[3];
            const individual = m[5];
            const checksum = m[6];

            const numberToCheck = `${dd}${mm}${yy}${individual}`;
            const mod31 = parseInt(numberToCheck, 10) % 31;
            const checksumChars = "0123456789ABCDEFHJKLMNPRSTUVWXY";
            ok = checksum === checksumChars[mod31];
        }

        if (ok) {
            this.$ssnInput.removeClass("is-invalid");
            if (this.$ssnError && this.$ssnError.length) this.$ssnError.hide().text("");
            return true;
        }

        // Invalid → show feedback in your existing placeholder
        this.$ssnInput.addClass("is-invalid");
        if (this.$ssnError && this.$ssnError.length) {
            this.$ssnError
                .text("The format of the personal identification number is not valid.")
                .show();
        }
        return false;
    },
});

export default publicWidget.registry.PortalExpenseModalMulti;
