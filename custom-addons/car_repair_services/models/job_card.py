# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
#  Part of Dhaval (https://www.upwork.com/freelancers/~01b41453a710f4c7c1).  #
#  See LICENSE file for full copyright and licensing details.                #
#                                                                            #
##############################################################################

import json
import ast

import requests
# from odoo.addons.account.models.account_tax import AccountTaxTotals
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
import logging
from odoo.tools.misc import formatLang
from collections import defaultdict
_logger = logging.getLogger(__name__)


from odoo import models, fields, api
from odoo.exceptions import ValidationError
from collections import defaultdict
    
    
class JobCard(models.Model):
    _name = 'job.card'
    _description = 'Job Card'
    _inherit = ['portal.mixin', 'product.catalog.mixin','mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = 'job_card_date desc, id desc'
    

    @api.depends('job_card_line.price_subtotal', 'job_card_line.price_tax', 'job_card_line.price_total')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for order in self:
            order = order.with_company(order.company_id)
            job_card_line = order.job_card_line.filtered(lambda x: not x.display_type)

            if order.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = order.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in job_card_line
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(order.currency_id, {}).get('amount_untaxed', 0.0)
                amount_tax = totals.get(order.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(job_card_line.mapped('price_subtotal'))
                amount_tax = sum(job_card_line.mapped('price_tax'))

            order.amount_untaxed = amount_untaxed
            order.amount_tax = amount_tax
            order.amount_total = order.amount_untaxed + order.amount_tax
            _logger.info(f"====totals job card==={order.amount_total}")
   
    @api.depends_context('lang')
    @api.depends('job_card_line.tax_id', 'job_card_line.price_unit', 'amount_total', 'amount_untaxed', 'currency_id')
    def _compute_tax_totals(self):
        
        for order in self:
            order = order.with_company(order.company_id)
            job_card_line = order.job_card_line.filtered(lambda x: not x.display_type)
            order.tax_totals = order.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in job_card_line],
                order.currency_id or order.company_id.currency_id,
            )
            _logger.info(f"=====tax total==={order.tax_totals}")

            
    @api.model
    def _get_default_non_gst_company(self):
        ''' Get the default non gst company'''
        company = self.env['res.company'].search([('vat','=',False)], limit=1)
        return company.id or self.env.company.id

    # def _get_product_catalog_order_data(self, products, **kwargs):
    #     res = super()._get_product_catalog_order_data(products, **kwargs)
    #     for product in products:
    #         res[product.id] |= {
    #             'price': product.standard_price,
    #         }
    #     return res
    
    # def _get_product_catalog_record_lines(self, product_ids):
    #     grouped_lines = defaultdict(lambda: self.job_card_line.browse([]))
    #     for line in self.job_card_line:
    #         if line.product_id.id not in product_ids:
    #             continue
    #         grouped_lines[line.product_id] |= line
    #     return grouped_lines



    active = fields.Boolean(default=True, string="Active")
    tax_ids = fields.Many2many('account.tax', string='Taxes')
    name = fields.Char(string='Job Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, change_default=True, index=True, tracking=1)
    street =  fields.Char(string="Street", related="partner_id.street", depends=['partner_id.street'], store=True)
    mobile =  fields.Char(string="Mobile", related="partner_id.mobile", depends=['partner_id.mobile'], store=True)
    job_card_date = fields.Date(string='Job Card Date', default=fields.Date.today)
    reg_no = fields.Char(string="Registration No.", related="partner_id.reg_no", depends=['partner_id.reg_no'], store=True)
    model_id = fields.Many2one(string="Model", related="partner_id.model_id", depends=['partner_id.model_id'], store=True)
    make_id = fields.Many2one(string="Make", related="partner_id.make_id", depends=['partner_id.make_id'], store=True)
    variant_id = fields.Many2one(string="Variant", related="partner_id.variant_id", depends=['partner_id.variant_id'], store=True)
    color_id = fields.Many2one(string="Color", related="partner_id.color_id", depends=['partner_id.color_id'], store=True)
    fuel_type = fields.Selection(related="partner_id.fuel_type", depends=['partner_id.fuel_type'], store=True)
    engine_no = fields.Char(string="Engine No.", related="partner_id.engine_no", depends=['partner_id.engine_no'], store=True)
    chassis_no = fields.Char(string="Chassis No.", related="partner_id.chassis_no", depends=['partner_id.chassis_no'], store=True)
    insurance_company = fields.Many2one(string="Insurance Company", related="partner_id.insurance_company", depends=['partner_id.insurance_company'], store=True)
    insurance_policy_no = fields.Char(string="Insurance Policy No.", related="partner_id.insurance_policy_no", depends=['partner_id.insurance_policy_no'], store=True)
    policy_expiry_date = fields.Date(string="Policy Expiry Date", related="partner_id.policy_expiry_date", depends=['partner_id.policy_expiry_date'], store=True)
    puc_expiry_date = fields.Date(string="PUC Expiry Date", related="partner_id.puc_expiry_date", depends=['partner_id.puc_expiry_date'], store=True)
    cng_expiry_date = fields.Date(string="CNG Testing Expiry Date", related="partner_id.cng_expiry_date", depends=['partner_id.cng_expiry_date'], store=True)
    run_km = fields.Char(string="Odometer(KM)")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assign', 'Assigned'),
        ('estimate', 'Estimated'),
        ('approve', 'Approved'),
        ('work', 'Working'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, tracking=2, default=lambda self: self.env.user)
    employee_id = fields.Many2one('hr.employee', string='Mechanic', index=True, tracking=2)
    # currency_id = fields.Many2one('res.currency',string="Currency",  default=lambda self: self.env.user.company_id.currency_id,required=True)
    currency_id = fields.Many2one('res.currency',ondelete="restrict",default=lambda self: self.env.user.company_id.currency_id)
    job_card_line = fields.One2many('job.card.line', 'job_card_id', string='Job Card Lines', copy=True, auto_join=True)
    job_card_image_line = fields.One2many('job.card.image', 'job_card_id', string='Job Card Image Lines', copy=True, auto_join=True)
    note = fields.Text()

    
    tax_totals = fields.Json(compute="_compute_tax_totals", readonly=True)
    # tax_totals_json = fields.Char(compute="_compute_tax_totals_json", readonly=True)
    # tax_totals = fields.Char(string="tax_totals",compute='_compute_tax_totals', exportable=False) 
    # formatted_amount_total = fields.Char(string="Total", compute='_compute_tax_totals', store=False)
    # formatted_amount_untaxed = fields.Char(string="Untaxed Amount", compute='_compute_tax_totals', store=False)
    # formatted_amount_tax = fields.Char(string="Tax", compute='_compute_tax_totals', store=False)

    
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, compute='_compute_amounts', tracking=5)
    amount_tax = fields.Monetary(string='Taxes', store=True, compute='_compute_amounts')
    amount_total = fields.Monetary(string='Total', store=True, compute='_compute_amounts', tracking=4)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=_get_default_non_gst_company)
    estimate_count = fields.Integer(string='Estimate Count', compute='_get_estimate_count')

    # @api.constrains('partner_id')
    # def _check_partner_id(self):
    #     if self.partner_id:
    #         existJob = self.search_count([('state','not in',('done','cancel')),('id','!=', self.id)])
    #         if existJob:
    #             raise UserError(_('You cannot chnage the Customer!'))

    @api.constrains('reg_no')
    def _check_jobcard_status(self):
        if self.reg_no:
            existJob = self.search_count([('reg_no','=',self.reg_no),('state','not in',('done','cancel')),('id','!=', self.id)])
            if existJob:
                raise UserError(_('You cannot create New Job Card. Please done existing Job Card first!'))

    # @api.constrains('run_km')
    # def _check_run_km(self):
    #     if self.run_km:
    #         existJob = self.search_count([('state','not in',('done','cancel')),('id','!=', self.id)])
    #         if existJob:
    #             raise UserError(_('You cannot chnage the Odometer(KM)!'))


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                seq_date = None
                if 'date_order' in vals:
                    seq_date = fields.Datetime.context_timestamp(self, fields.Date.to_datetime(vals['job_card_date']))
                vals['name'] = self.env['ir.sequence'].next_by_code('job.card', sequence_date=seq_date) or _('New')
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('partner_id') and self.state in ('done','cancel'):
            raise UserError(_('You cannot chnage the Customer!'))
        if vals.get('run_km') and self.state in ('done','cancel'):
            raise UserError(_('You cannot chnage the Odometer(KM)!'))
        return super(JobCard, self).write(vals)

    def action_draft(self):
        orders = self.filtered(lambda s: s.state in ['cancel'])
        return orders.write({'state': 'draft'})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def send_job_ard_whatsapp_notification(self):
        ''' This method is called from a cron job.
        It is used to send whatsapp notification for insurance expiry.
        '''
        whatsappURL = self.env['ir.config_parameter'].sudo().get_param('car_repair_services.whatsapp_url')
        whatsappInstance = self.env['ir.config_parameter'].sudo().get_param('car_repair_services.whatsapp_instance')
        whatsappToken = self.env['ir.config_parameter'].sudo().get_param('car_repair_services.whatsapp_token')
        messageText = "Hello %s,\n\nYour car job card created.\n\n(Yash Motors)\nThank you"%(self.partner_id.name)
        url = "%snumber=%s&type=text&message=%s&instance_id=%s&access_token=%s"%(
            whatsappURL,
            self.mobile.replace(" ", '').replace('+', ''),
            messageText,
            whatsappInstance,
            whatsappToken)
        response = requests.get(url)
        self.message_post(body=_("Whatsapp - Message Sent:" + messageText))

    def action_assign(self):
        if not self.employee_id:
            raise UserError(_("Please Select Assign To."))
        self.send_job_ard_whatsapp_notification()
        return self.write({'state': 'assign'})

    # def action_check(self):
    #     return self.write({'state': 'check'})

    def action_create_estimate(self):
        if self.job_card_line:
            sale_order = self.env['sale.order'].create({
                'partner_id': self.partner_id.id,
                'payment_term_id': self.partner_id.property_payment_term_id.id,
                'client_order_ref': self.partner_id.ref,
                'company_id': self.company_id.id,
                'job_card_id': self.id,
                'note': self.note,
            })
            saleLineObj = self.env['sale.order.line']
            for line in self.job_card_line:
                lineDict = {
                            'categ_id': line.categ_id.id or False,
                            'product_id': line.product_id.id,
                            'name': line.name if line.name else line.product_id.name,
                            'product_uom_qty': line.product_uom_qty,
                            'product_uom': line.product_uom.id or line.product_id.uom_id.id,
                            'price_unit': line.price_unit,
                            'labour_charge': line.labour_charge,
                            'tax_id': [(6, 0, line.tax_id.ids)],
                            'order_id': sale_order.id,
                            'company_id': line.company_id.id,
                            'display_type': line.display_type,
                }
                print("lineDict================",lineDict)
                saleLineObj.create(lineDict)
            if sale_order:
                self.write({'state': 'estimate'})
                return {
                        'name':_("Estimate"),
                        'view_mode': 'form',
                        'view_id': False,
                        'view_type': 'form',
                        'res_model': 'sale.order',
                        'res_id': sale_order.id,
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'domain': '[]',
                }
    def _update_order_line_info(self, product_id, quantity, **kwargs):
        """
        Add or update product in job card line based on quantity.
        :param int product_id: The product, as a `product.product` id.
        :return: The created or updated line.
        """
        self.ensure_one()
        product = self.env['product.product'].browse(product_id)
        _logger.info(f"=====unit price 1===:{product.lst_price}")
        # Get price and tax
        unit_price = 100.00
        _logger.info(f"=====unit price 2===:{unit_price}")
        
        taxes = product.taxes_id

        # Find existing line
        pol = self.job_card_line.filtered(lambda line: line.product_id.id == product_id)

        if pol:
            if quantity != 0:
                pol.update({
                    'product_uom_qty': quantity,
                    'price_unit': unit_price,
                    'tax_id': [(6, 0, taxes.ids)],
                })
            else:
                pol.unlink()
                return None
        elif quantity > 0:
            pol = self.env['job.card.line'].create({
                'job_card_id': self.id,
                'product_id': product_id,
                'product_uom_qty': quantity,
                'price_unit': unit_price,
                'tax_id': [(6, 0, taxes.ids)],
            })

        return pol


    
    @api.depends('state')
    def _get_estimate_count(self):
        for rec in self:
            rec.estimate_count = self.env['sale.order'].search_count([('job_card_id','=',rec.id)])

    def action_view_estimate(self):
        saleOrder = self.env['sale.order'].search([('job_card_id','=',self.id)])
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        if len(saleOrder) > 1:
            action['domain'] = [('id', 'in', saleOrder.ids)]
        elif len(saleOrder) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = saleOrder.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_working(self):
        return self.write({'state': 'work'})

    def action_done(self):
        return self.write({'state': 'done'})

    def print_product_pre_inspection(self):
        preInspectionData = []
        for line in self.mapped('job_card_line'):
            for preInspection in line.product_id.mapped('pre_inspection_line').sorted(key=lambda r: r.sequence):
                preInspectionData.extend([preInspection.pre_inspection_id.name, preInspection.value_id.name])
        return [preInspectionData[x:x+4] for x in range(0, len(preInspectionData),4)]

    def _get_product_catalog_order_data(self, products, **kwargs):
        res = super()._get_product_catalog_order_data(products, **kwargs)
        for product in products:
            res[product.id] |= {
                'price': product.lst_price or 0.0,
            }
        return res
    
    def _get_product_catalog_record_lines(self, product_ids):
        grouped_lines = defaultdict(lambda: self.env['job.card.line'])
        for line in self.job_card_line:
            if line.product_id.id not in product_ids:
                continue
            grouped_lines[line.product_id] |= line
        return grouped_lines
    
    # def action_open_job_card_with_inspection_popup(self):
    #     inspection_obj = self.env['job.card.inspection']
    #     inspection_id = inspection_obj.search([('job_card_id', '=', self.id)], limit=1)

    #     if not inspection_id:
    #         inspection_id = inspection_obj.create({'job_card_id': self.id})
    
    def action_open_job_card_with_inspection_popup(self):
        return {
            'name': 'Job Card Inspection',
            'type': 'ir.actions.act_window',
            'res_model': 'job.card',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'create': False}
        }

        return {
            'name': 'Job Card With Inspection',
            'type': 'ir.actions.act_window',
            'res_model': 'job.card.inspection',
            'res_id': inspection_id.id,
            'view_mode': 'form',
            'target': 'new', # 'new' opens it as a popup/modal
        }

    
class JobCardLine(models.Model):
    _name = 'job.card.line'
    _description = 'Job Card Line'
    _order = 'sequence, id'

    def _convert_to_tax_base_line_dict(self, **kwargs):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.

        :return: A python dictionary.
        """
        # rrr = **kwargs
        _logger.info(f"====helloooo")
        self.ensure_one()
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=self.job_card_id.partner_id,
            currency=self.job_card_id.currency_id,
            product=self.product_id,
            taxes=self.tax_id,
            price_unit=self.price_unit,
            quantity=self.product_uom_qty,
            discount=self.discount,
            price_subtotal=self.price_subtotal,
            **kwargs,
        )
    
    
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'labour_charge')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = (line.price_unit) * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.job_card_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.job_card_id.partner_id)
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

    
    
    state=fields.Selection(
        related='job_card_id.state',
        string="Job Card Status",
        copy=False,store=True,precompute=True
    )
    sequence = fields.Integer(string='Sequence', default=10)
    model_id = fields.Many2one(string="Model", related="job_card_id.model_id", depends=['job_card_id.model_id'], store=True)
    categ_id = fields.Many2one('product.category', string='Category', change_default=True, ondelete='restrict')
    product_ids = fields.Many2many('product.product', string='Product', compute="_compute_prroduct_ids")
    product_id = fields.Many2one('product.product', string='Product', domain="[('sale_ok', '=', True)]",
        change_default=True, ondelete='restrict')
    name = fields.Text(string='Description')
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]", ondelete="restrict")
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    
    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    # currency_id = fields.Many2one(related='job_card_id.currency_id', depends=['job_card_id.currency_id'], store=True, string='Currency')
    currency_id = fields.Many2one('res.currency', string='Currency',compute="_compute_currency_id",store=True,readonly=False,precompute=True,default=lambda self: self.env.company.currency_id.id)
    
    company_id = fields.Many2one(related='job_card_id.company_id', string='Company', store=True, index=True)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal',currency_field='currency_id', store=True,default=0.0 )
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total',currency_field='currency_id', store=True,default=0.0 )
    tax_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False}, check_company=True)
    job_card_id = fields.Many2one('job.card', string='Job Card')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    labour_charge = fields.Float(string="Labour Charge",default=0.0)
    job_card_inspection_line_ids = fields.One2many(
        'job.card.line.inspection',
        'job_card_line_id',
        string='Pre-Inspection Items',
    )
    
    @api.model
    def create(self, vals):
        line = super().create(vals)
        line._create_inspection_lines()
        return line

    def write(self, vals):
        res = super().write(vals)
        if 'product_id' in vals:
            for line in self:
                line.job_card_inspection_line_ids.unlink()
                line._create_inspection_lines()
        return res

    def _create_inspection_lines(self):
        ConfirmOption = self.env['confirm.inspection.option']
        if self.product_id and self.product_id.pre_inspection_line:
            for item in self.product_id.pre_inspection_line:
                # Extract and split the value options from value_id.name
                value_options = [opt.strip().lower() for opt in item.value_id.name.split('/') if opt.strip()]
                # confirm_option_id = []
                _logger.info(f"====value_options=====:{value_options}")
                _logger.info(f"====item.value=====:{item.value_id.id}")
                confirm_option_ids = []
                for option in value_options:
                    confirm_option = ConfirmOption.search([('name', '=', option)], limit=1)
                    _logger.info(f"====confirm_option=====:{confirm_option}")
                    _logger.info(f"====item.value=====:{item.value_id.id}")
                    if not confirm_option:
                        confirm_option = ConfirmOption.create({
                            'name': option,
                            'value_id': item.value_id.id,
                        })
                    confirm_option_ids.append(confirm_option.id)
                    _logger.info(f"====confirm_option if=====:{confirm_option}")

                # confirm_option_id = confirm_option_ids[0] if confirm_option_ids else False
                # Create the job.card.line.inspection line
                self.env['job.card.line.inspection'].create({
                    'job_card_line_id': self.id,
                    'pre_inspection_id': item.pre_inspection_id.id,
                    'value_id': item.value_id.id,
                    # 'confirm_inspection': confirm_option_ids,
                #    'confirm_inspection': [(6, 0, confirm_option_ids)],
                })
    
    
    @api.depends('job_card_id.currency_id')
    def _compute_currency_id(self):
        for rec in self:
            rec.currency_id = rec.job_card_id.currency_id or self.env.company.currency_id

    @api.onchange('product_id')
    def product_id_change(self):
        self.product_uom = self.product_id.uom_id
        self.name = self.product_id.name
        taxes = self.product_id.taxes_id.filtered(lambda t: t.company_id == self.env.company)
        self.tax_id = taxes and taxes.ids or False
        print("Labour===========",self.product_id.labour_charge)
        self.labour_charge = int(self.product_id.labour_charge)

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.job_card_id.partner_id:
            product = self.product_id.with_context(
                lang=self.job_card_id.partner_id.lang,
                partner=self.job_card_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.job_card_id.job_card_date,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = product._get_tax_included_unit_price(
                self.company_id,
                self.job_card_id.currency_id,
                self.job_card_id.job_card_date,
                'sale',
                fiscal_position=self.env.context.get('fiscal_position'),
                product_price_unit=None,
                product_currency=self.job_card_id.currency_id
            )

    def _prepare_base_line_for_taxes_computation(self, **kwargs):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.

        :return: A python dictionary.
        """
        self.ensure_one()
        return self.env['account.tax']._prepare_base_line_for_taxes_computation(
            self,
            **{
                'tax_ids': self.tax_id,
                'quantity': self.product_uom_qty,
                'partner_id': self.job_card_id.partner_id,
                'currency_id': self.job_card_id.currency_id or self.job_card_id.company_id.currency_id,
                # 'rate': self.job_card_id.currency_rate,
                **kwargs,
            },
        )
        
        
    def action_add_from_catalog(self):
        job_card = self.env['job.card'].browse(
            self.env.context.get('order_id'))
        return job_card.action_add_from_catalog()

    def _get_product_catalog_lines_data(self):
        catalog_info = {
            'quantity': self.product_uom_qty,
            'price': self.price_unit,
        }
        return catalog_info

    
    
    
    
class JobCardImage(models.Model):
    _name = 'job.card.image'
    _description = 'Job Card Image'

    name = fields.Char(string='Notes')
    sequence = fields.Integer(string='Sequence', default=10)
    photo_type = fields.Selection([
        ('left', "Left"),
        ('right', "Right"),
        ('front', "Front"),
        ('top', "Top"),
        ('rear', "Rear"),
        ('dashboard', "Dashboard")
        ], string="Type")
    photo_1920 = fields.Image("Photos", copy=False, attachment=True, max_width=1024, max_height=1024)
    job_card_id = fields.Many2one('job.card', string='Job Card')
    
class JobCardLineInspection(models.Model):
    _name = 'job.card.line.inspection'
    _description = 'Job Card Line Inspection'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    job_card_line_id = fields.Many2one(
        'job.card.line', 
        string='Job Card Line',
        required=True,
        ondelete='cascade'
    )
    pre_inspection_id = fields.Many2one(
        'pre.inspection',
        string='Pre-Inspection Item',
        required=True
    )
    value_id = fields.Many2one(
        'pre.inspection.value',
        string='Expected Value',
        required=True
    )
    confirm_inspection = fields.Many2many(
        'confirm.inspection.option',
        string='Confirmed Value'
    )
    notes = fields.Text(string='Notes')
    
    
    
class ConfirmInspectionOption(models.Model):
    _name = 'confirm.inspection.option'
    _description = 'Confirm Inspection Option'

    name = fields.Char(string='Option Name', required=True)
    value_id = fields.Many2one('pre.inspection.value', string='Pre-Inspection Value', required=True, ondelete='cascade')