// Example JavaScript in your custom module
odoo.define('car_repair_services.JobCard', function (require) {
    "use strict";

    var rpc = require('web.rpc');
    var core = require('web.core');

    var JobCardController = require('car_repair_services.JobCardController').include({
        _onAddFromCatalog: function (ev) {
            var self = this;
            var productId = $(ev.currentTarget).data('product-id');
            var quantity = 1; // Adjust as needed

            rpc.query({
                model: 'job.card',
                method: '_update_order_line_info',
                args: [productId, quantity],
            }).then(function (result) {
                if (result.reload) {
                    self.reload(); // Reload the view to reflect changes
                } else {
                    // Update the UI manually if needed
                    self.render(); // Or update specific fields
                }
            });
        },
    });
});