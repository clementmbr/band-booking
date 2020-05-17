// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
odoo.define("web_form_background_color.FormBackgroundColor", function(require) {
    "use strict";

    var FormRenderer = require("web.FormRenderer");

    FormRenderer.include({
        /**
         * Wrap form into a div with special class
         * @override
         */
        _updateView: function() {
            this._super.apply(this, arguments);

            var div_form_sheet_bg = this.$el.children().not(".oe_chatter")[0];

            if (this.has_sheet && this.state.model === "crm.lead") {
                div_form_sheet_bg.classList.remove("o_form_sheet_bg");
                if (this.state.data.type === "opportunity") {
                    div_form_sheet_bg.classList.add("o_form_sheet_bg_opportunity");
                } else {
                    div_form_sheet_bg.classList.add("o_form_sheet_bg_lead");
                }
            } else if (this.has_sheet && this.state.model === "event.event") {
                div_form_sheet_bg.classList.remove("o_form_sheet_bg");
                div_form_sheet_bg.classList.add("o_form_sheet_bg_event");
            }
            // NOT WORKING :
            // this.$el.children().not('.oe_chatter')[0].style.backgroundColor = "red";
        },
    });
});
