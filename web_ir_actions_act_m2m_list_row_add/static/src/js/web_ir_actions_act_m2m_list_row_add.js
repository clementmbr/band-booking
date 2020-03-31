// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
odoo.define('web_ir_actions_act_m2m_list_row_add.ir_actions_act_m2m_list_row_add', function (require) {
    "use strict";

    var ActionManager = require('web.ActionManager');
    var AbstractField = require('web.AbstractField');
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
         * Handle 'ir.actions.act_m2m_list_row_add' action
         * @returns {$.Promise}
         */
        _executeAddRecord: function(action, options) {
            var self = this;

            console.log("action", action)

            // TODO : Remplacer 'this' par l'objet JS du champs m2m définit par 'action.field_name'

            // Create a SelectCreateDialog pop-up
            var domain = [["is_structure", "=", false]];
            new dialogs.SelectCreateDialog(this, {
                res_model: action.res_model, // res.partner
                domain: domain.concat(["!", ["id", "in", action.field.value.res_ids]]), // [ ["is_structure", "=", false] , "!", ["id", "in", [11, 53, 54, 49, 12, 40] ]
                context: action.context, // dico ressemblant à 'self.env.context' => déjà dans action.context
                title: _t("Add: ") + action.field.string, // Related Contacts
                no_create: action.no_create, // false
                // fields_view: this.attrs.views.form, // undefined
                on_selected: function (records) {
                    var resIDs = _.pluck(records, 'id');
                    var newIDs = _.difference(resIDs, action.field.value.res_ids);
                    console.log("self", self);
                    // console.log("_setValue()", _setValue);
                    if (newIDs.length) {
                        var values = _.map(newIDs, function (id) {
                            return {id: id};
                        });
                        self._setValue({
                            operation: 'ADD_M2M',
                            ids: values,
                        });
                    }
                }// function appelée quand on clique sur le bouton 'Select' de la pop-up
            }).open();

            return $.when();
        },

    });

});
