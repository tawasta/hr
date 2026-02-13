/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.PortalExpenseTempus = publicWidget.Widget.extend({
    selector: ".o_portal_wrap",

    start() {
        this._super(...arguments);

        const $modal = $("#portalCreateExpenseModal");
        if (!$modal.length) return;

        // Init only when modal is visible (same pattern as your working module)
        $modal.on("shown.bs.modal", () => {
            this._initTempusInside($modal);
        });

        return this._super(...arguments);
    },

    _initTempusInside($root) {
        if (!$root || !$root.length) return;

        $root.find("input.datetimepicker-input").each(function () {
            const el = this;

            // Prevent multiple inits
            if (el.dataset.tdInitialized === "1") return;
            el.dataset.tdInitialized = "1";

            if (typeof tempusDominus === "undefined") {
                console.error("Tempus Dominus is not loaded.");
                return;
            }

            // Create instance on the INPUT (same as your working example)
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
                    buttons: {
                        today: true,
                        clear: true,
                        close: true,
                    },
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
                localization: {
                    format: "dd.MM.yyyy",
                },
            });

            // Make the calendar icon open the picker
            const $group = $(el).closest(".input-group");
            const $btn = $group.find(".input-group-text").first();
            if ($btn && $btn.length) {
                $btn.off("click.portalExpenseTempus").on(
                    "click.portalExpenseTempus",
                    () => {
                        try {
                            instance.show();
                        } catch (e) {
                            // If API differs in minor versions, fallback to focusing the input
                            el.focus();
                        }
                    }
                );
            }
        });
    },
});

export default publicWidget.registry.PortalExpenseTempus;
