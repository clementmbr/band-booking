// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
odoo.define('web_ir_actions_act_m2m_list_row_add.ir_actions_act_m2m_list_row_add', function (require) {
    "use strict";

    var ActionManager = require('web.ActionManager');
    var dialogs = require('web.view_dialogs');
    var core = require('web.core');

    var _t = core._t;

    ActionManager.include({

        /**
         * Intersept action handling to detect extra action type
         * @override
         */
        _handleAction: function (action, options) {
            if (action.type === 'ir.actions.act_m2m_list_row_add') {
                return this._executeAddRecord(action, options);
            }

            return this._super.apply(this, arguments);
        },

        /**
         * Fonction to set Value to a m2m field (inspired by AbstractField._setValue in core)
         * https://github.com/odoo/odoo/blob/12.0/addons/web/static/src/js/fields/abstract_field.js#L472
         * @private
         * @param {any} value
         * @returns {Deferred}
         */
        action_setValue: function (action, value) {
            var def = $.Deferred();
            var changes = {};
            changes[action.field.name] = value;
            this.trigger_up('field_changed', {
                dataPointID: "res.partner_27", // TODO : find a way to catch this field ID...
                changes: changes,
                viewType: 'form',
                notifyChange: true,
                // doNotSetDirty: undefined, // unuseful, if commented in core, it runs the same way.
                // allowWarning: undefined,
                // onSuccess: def.resolve.bind(def),
                // onFailure: def.reject.bind(def),
            });
            return def;
        },

        /**
         * Handle 'ir.actions.act_m2m_list_row_add' action
         * @returns {$.Promise}
         */
        _executeAddRecord: function(action, options) {
            var self = this;
            console.log("action", action);

            var domain_string = action.field.domain
                .replace(/\(/g, "[")
                .replace(/\)/g, "]")
                .replace(/\'/g, "\"")
                .toLowerCase()
            var domain = JSON.parse(domain_string);

            // Create a SelectCreateDialog pop-up (inspired by _onAddRecord() in relational_field.js)
            // https://github.com/odoo/odoo/blob/12.0/addons/web/static/src/js/fields/relational_fields.js#L1609
            new dialogs.SelectCreateDialog(this, {
                res_model: action.res_model, // == res.partner
                domain: domain.concat(["!", ["id", "in", action.field.value.res_ids]]), // == [ ["is_structure", "=", false] , "!", ["id", "in", [11, 53, 54, 49, 12, 40] ]
                context: action.context, // == 'self.env.context' -> already in action.context
                title: _t("Add: ") + action.field.string, // == 'Add: Related Contacts'
                no_create: action.no_create, // == false
                // fields_view: this.attrs.views.form, // undefined in core -> unuseful
                on_selected: function (records) { // function called when clicking on "Select"
                    var resIDs = _.pluck(records, 'id');
                    var newIDs = _.difference(resIDs, action.field.value.res_ids);
                    if (newIDs.length) {
                        var values = _.map(newIDs, function (id) {
                            return {id: id};
                        });
                        self.action_setValue(action, {
                            operation: 'ADD_M2M',
                            ids: values,
                        });
                    }
                }
            }).open();

            return $.when();
        },

    });

});
