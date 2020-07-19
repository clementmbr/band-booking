// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
odoo.define("web_calendar_defaultdate.CalendarDefaultDate", function(require) {
    "use strict";

    var AbstractRenderer = require("web.AbstractRenderer");

    AbstractRenderer.include({
        // TODO change date smallcalendar

        //
        /**
         * Find the first date_begin of the upcomming events
         */
        _go_to_lowest_date: function() {
            return $.when(
                this._rpc({
                    model: "event.event",
                    method: "search_read",
                    fields: ["date_begin", "date_end"],
                    domain: [["state", "!=", "cancel"]],
                }),
                this.$calendar
            ).then(function(all_dates, $calendar) {
                var date_lowest = new Date(all_dates[all_dates.length - 1].date_begin);
                var today = new Date();

                for (var i = all_dates.length - 1; i >= 0; i--) {
                    var date_begin = new Date(all_dates[i].date_begin);
                    var date_end = new Date(all_dates[i].date_end);

                    if (date_lowest > date_begin && today <= date_end)
                        date_lowest = date_begin;
                }

                $calendar.fullCalendar("gotoDate", moment(date_lowest));
                console.log("date_lowest", date_lowest);
            });
        },

        /**
         * @override
         * @private
         * @returns {Deferred}
         */
        _render: function() {
            if (this.hijack_target_date !== 1) {
                this._go_to_lowest_date();
                this.hijack_target_date = 1;
            }

            // Render Calendar view
            var scrollTop = this.$calendar.find(".fc-scroller").scrollTop();
            this._renderFilters();
            this.$calendar.appendTo("body");
            if (scrollTop) {
                this.$calendar.fullCalendar("reinitView");
            } else {
                this.$calendar.fullCalendar("render");
            }
            this._renderEvents();
            this.$calendar.prependTo(this.$(".o_calendar_view"));

            // FIXME: These functions are realised BEFORE the _go_to_lowest_date()
            // So the final calendar view does not display the Events and the Filters

            return this._super.apply(this, arguments);
        },
    });
});
