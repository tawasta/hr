/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.PortalExpenseModalMulti = publicWidget.Widget.extend({
    selector: ".o_portal_wrap",

    start() {
        this._super(...arguments);

        this.$modal = $("#portalCreateExpenseModal");
        if (!this.$modal.length) return this._super(...arguments);

        this.$modal.on("shown.bs.modal", () => {
            const $wrap = this.$modal.find(".js-expense-lines-cards");
            if ($wrap.length && !$wrap.find(".js-expense-line-card").length) {
                this._addLine(true);
            }
            this._initTempusInside(this.$modal);
            this._updateLineNumbers();
        });

        this.$modal.on("click", ".js-add-expense-line", (ev) => {
            ev.preventDefault();
            this._addLine(true);
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

        return this._super(...arguments);
    },

    _nextIndex() {
        const $wrap = this.$modal.find(".js-expense-lines-cards");
        const current = parseInt($wrap.attr("data-next-index") || "1", 10);
        $wrap.attr("data-next-index", String(current + 1));
        return current;
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

        // Names become line_name_1 etc (from your logs)
        const name = ($card.find(`[name="line_name_${idx}"]`).val() || "")
            .toString()
            .trim();
        const qty = ($card.find(`[name="line_quantity_${idx}"]`).val() || "")
            .toString()
            .trim();
        const unit = ($card.find(`[name="line_price_unit_${idx}"]`).val() || "")
            .toString()
            .trim();

        let summary = name ? name : "New line";
        if (qty && unit) summary += ` · ${qty} × ${unit}`;
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
});

export default publicWidget.registry.PortalExpenseModalMulti;
