# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
#  Part of Dhaval (https://www.upwork.com/freelancers/~01b41453a710f4c7c1).  #
#  See LICENSE file for full copyright and licensing details.                #
#                                                                            #
##############################################################################

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    reg_no = fields.Char(string="Registration No.", related="partner_id.reg_no", depends=['partner_id.reg_no'], store=True)
    model_id = fields.Many2one(string="Model", related="partner_id.model_id", depends=['partner_id.model_id'], store=True)
    make_id = fields.Many2one(string="Make", related="partner_id.make_id", depends=['partner_id.make_id'], store=True)
    variant_id = fields.Many2one(string="Variant", related="partner_id.variant_id", depends=['partner_id.variant_id'], store=True)
    color_id = fields.Many2one(string="Color", related="partner_id.color_id", depends=['partner_id.color_id'], store=True)
    fuel_type = fields.Selection(related="partner_id.fuel_type", depends=['partner_id.fuel_type'], store=True)
    job_card_id = fields.Many2one('job.card', string='Job Card')
    run_km = fields.Char(string="Odometer(KM)", related="job_card_id.run_km", depends=['job_card_id.run_km'], store=True)

    def _prepare_confirmation_values(self):
        result = super(SaleOrder, self)._prepare_confirmation_values()
        if result and self.job_card_id and self.job_card_id.state == 'estimate':
            self.job_card_id.state = 'approve'
        return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('categ_id', 'model_id')
    def _compute_prroduct_ids(self):
        labourCategId = self.env.ref('car_repair_services.product_category_labour')
        allCarCategId = self.env.ref('car_repair_services.product_category_all_car')
        for line in self:
            if line.categ_id and line.categ_id.parent_id in [labourCategId, allCarCategId]:
                line.update({
                    'product_ids': self.env['product.product'].search([('categ_id', '=', line.categ_id.id)]).ids
                })
            else:
                domain = []
                if line.categ_id:
                    domain.append(('categ_id', '=', line.categ_id.id))
                line.update({
                    'product_ids': self.env['product.product'].search(domain + [('model_ids', 'in', line.model_id.id)]).ids
                })

    categ_id = fields.Many2one('product.category', string='Categories', change_default=True, ondelete='restrict')
    model_id = fields.Many2one(string="Model", related="order_id.partner_id.model_id", depends=['order_id.partner_id.model_id'], store=True)
    product_ids = fields.Many2many('product.product', string='Product', compute="_compute_prroduct_ids")
    approval = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ], string='Approval', default='yes')
    labour_charge = fields.Char(string="Labour Charge")

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return

        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            self.update({
                'product_uom': self.product_id.uom_id,
                'product_uom_qty': self.product_uom_qty or 1.0
            })

        # self._update_description()
        # self._update_taxes()

        if self.product_id and self.product_id.labour_charge:
            self.labour_charge = int(self.product_id.labour_charge)

        product = self.product_id
        if product and product.sale_line_warn != 'no-message':
            if product.sale_line_warn == 'block':
                self.product_id = False
            return {
                'warning': {
                    'title': _("Warning for %s", product.name),
                    'message': product.sale_line_warn_msg,
                }
            }

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'labour_charge')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            if line.labour_charge:
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'] + int(line.labour_charge),
                    'price_subtotal': taxes['total_excluded'] + int(line.labour_charge),
                })
            else:
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })
