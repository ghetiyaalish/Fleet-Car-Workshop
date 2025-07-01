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

_logger = logging.getLogger(__name__)


class JobCard(models.Model):
    _name = 'job.card'
    _description = 'Job Card'
    _inherit = ['portal.mixin', 'product.catalog.mixin','mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = 'job_card_date desc, id desc'
    

    def _compute_amounts(self):
        """Compute order totals (untaxed, tax, total)."""
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.job_card_line:
                if line.display_type:
                    continue
                    
                # Calculate line amounts including labour charge
                line_subtotal = line.price_subtotal
                if line.labour_charge:
                    try:
                        line_subtotal += float(line.labour_charge)
                    except (ValueError, TypeError):
                        pass
                
                amount_untaxed += line_subtotal
                amount_tax += line.price_tax
            
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.depends('tax_totals')
    def _compute_tax_totals_json(self):
        for order in self:
            if not order.tax_totals:
                # Provide a complete empty structure with all required fields
                order.tax_totals_json = json.dumps({
                    'amount_total': 0.0,
                    'amount_untaxed': 0.0,
                    'amount_tax': 0.0,
                    'groups_by_subtotal': [],
                    'subtotals': [],
                    'subtotals_order': [],
                })
                continue

            tax_totals_dict = order.tax_totals

            # Handle string-formatted dictionaries
            if isinstance(tax_totals_dict, str):
                try:
                    tax_totals_dict = json.loads(tax_totals_dict)
                except json.JSONDecodeError:
                    try:
                        tax_totals_dict = ast.literal_eval(tax_totals_dict)
                    except Exception:
                        # Provide complete empty structure on error
                        order.tax_totals_json = json.dumps({
                            'amount_total': 0.0,
                            'amount_untaxed': 0.0,
                            'amount_tax': 0.0,
                            'groups_by_subtotal': [],
                            'subtotals': [],
                            'subtotals_order': [],
                        })
                        continue

            safe_totals = tax_totals_dict.copy()
            
            # Ensure required numeric fields exist
            for key in ['amount_total', 'amount_untaxed', 'amount_tax']:
                safe_totals[key] = float(safe_totals.get(key, 0.0))
                
            # Ensure required list fields exist and are iterable
            for key in ['groups_by_subtotal', 'subtotals', 'subtotals_order']:
                if key not in safe_totals or not isinstance(safe_totals.get(key), (list, tuple)):
                    safe_totals[key] = []

            order.tax_totals_json = json.dumps(safe_totals)
        

    @api.depends('job_card_line.price_subtotal', 'job_card_line.tax_id', 'currency_id', 'company_id')
    def _compute_tax_totals(self):
        for order in self:
            if not order.job_card_line:
                # Provide complete empty structure instead of False
                order.tax_totals = {
                    'amount_total': 0.0,
                    'amount_untaxed': 0.0,
                    'amount_tax': 0.0,
                    'groups_by_subtotal': [],
                    'subtotals': [],
                    'subtotals_order': [],
                }
                continue
                
            currency = order.currency_id or order.company_id.currency_id
            amount_untaxed = 0.0
            tax_groups = {}
            ungrouped_taxes = {
                'name': 'Ungrouped Taxes',
                'amount': 0.0,
                'base': 0.0
            }

            for line in order.job_card_line.filtered(lambda l: not l.display_type):
                price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                try:
                    labour_charge = float(line.labour_charge or 0.0)
                except (ValueError, TypeError):
                    labour_charge = 0.0

                taxes = line.tax_id.compute_all(
                    price_unit,
                    currency,
                    line.product_uom_qty,
                    product=line.product_id,
                    partner=order.partner_id,
                )

                subtotal = taxes['total_excluded'] + labour_charge
                amount_untaxed += subtotal

                for tax in taxes['taxes']:
                    tax_name = tax.get('name') or 'Tax'
                    tax_groups.setdefault(tax_name, {
                        'amount': 0.0,
                        'base': 0.0,
                    })
                    tax_groups[tax_name]['amount'] += tax['amount']
                    tax_groups[tax_name]['base'] += subtotal

            # Include ungrouped taxes if any
            if ungrouped_taxes['amount']:
                tax_groups[0] = ungrouped_taxes

            amount_tax = sum(t['amount'] for t in tax_groups.values())
            total = amount_untaxed + amount_tax

            # Define default subtotals structure
            default_subtotals = [
                {
                    'name': 'Untaxed Amount',
                    'amount': amount_untaxed,
                    'formatted_amount': formatLang(order.env, amount_untaxed, currency_obj=currency).replace('\xa0', ' '),
                },
                {
                    'name': 'Taxes',
                    'amount': amount_tax,
                    'formatted_amount': formatLang(order.env, amount_tax, currency_obj=currency).replace('\xa0', ' '),
                },
            ]

            order.tax_totals = {
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': total,
                'formatted_amount_total': formatLang(order.env, total, currency_obj=currency).replace('\xa0', ' '),
                'formatted_amount_untaxed': formatLang(order.env, amount_untaxed, currency_obj=currency).replace('\xa0', ' '),
                'formatted_amount_tax': formatLang(order.env, amount_tax, currency_obj=currency).replace('\xa0', ' '),
                'groups_by_subtotal': [{
                    'name': tax_name,
                    'amount': data['amount'],
                    'base': data['base'],
                    'formatted_amount': formatLang(order.env, data['amount'], currency_obj=currency).replace('\xa0', ' '),
                    'formatted_base': formatLang(order.env, data['base'], currency_obj=currency).replace('\xa0', ' '),
                } for tax_name, data in tax_groups.items()],
                'subtotals': default_subtotals,
                'subtotals_order': [sub['name'] for sub in default_subtotals],
                'total_included': total,
            }
            
    @api.model
    def _get_default_non_gst_company(self):
        ''' Get the default non gst company'''
        company = self.env['res.company'].search([('vat','=',False)], limit=1)
        return company.id or self.env.company.id


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

    
    # tax_totals = fields.Json(compute="_compute_tax_totals", readonly=True)
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


class JobCardLine(models.Model):
    _name = 'job.card.line'
    _description = 'Job Card Line'
    _order = 'sequence, id'

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

    def action_add_from_catalog(self):
        # If called from job.card.line, map to its parent job_card_id
        job_card = self.env['job.card'].browse(self.env.context.get('order_id'))
        # _logger.info(f'----------------------JOB CARD--------------{job_card.currency_id}')
        return job_card.action_add_from_catalog()


    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Product',
    #         'res_model': 'product.product',
    #         'view_mode': 'kanban',
    #         'target': 'current',
    #         'context': {
    #             'default_job_card_id': job_card.id,
    #             'default_currency_id': job_card.currency_id.id,
    #             'default_partner_id': job_card.partner_id.id,
                
    #         },
    #         'domain': [('sale_ok', '=', True)],
    #     }
    
    # def action_add_from_catalog(self):
    #     job_card = self.job_card_id if self._name == 'job.card.line' else self
    #     _logger.info(f'--JOB CARD--{job_card}')
    #     job_card.ensure_one()

    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Product Catalog',
    #         'res_model': 'product.product',
    #         'view_mode': 'tree,kanban,form',
    #         'views': [
    #             (False, 'tree'),  # Left-side category tree
    #             (False, 'kanban'),  # Right-side product grid
    #             (False, 'form')
    #         ],
    #         'target': 'current',
    #         'context': {
    #             'default_job_card_id': job_card.id,
    #             'default_currency_id': job_card.currency_id.id,
    #             'default_partner_id': job_card.partner_id.id,
    #             'search_default_filter_sale_ok': True,
    #             'catalog_view': True,  # Flag to enable custom JS
    #         },
    #         'domain': [('sale_ok', '=', True)],
    #     }
    
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

    # def action_add_from_catalog(self):
    #     jobCard = self.env['job.card'].browse(self.env.context.get('job_card_id'))
    #     _logger.info(f"=====jobcard===:{jobCard}")
    #     return jobCard.action_add_from_catalog()
    
    
    
    
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
    
    
class ProductProduct(models.Model):
    _inherit = 'product.product'

    # def action_add_to_job_card(self):
    #     job_card_id = self.env.context.get('default_job_card_id')
    #     if job_card_id:
    #         job_card = self.env['job.card'].browse(job_card_id)
    #         job_card.job_card_line.create({
    #             'job_card_id': job_card.id,
    #             'product_id': self.id,
    #             'name': self.name,
    #             'product_uom_qty': 1,
    #             'product_uom': self.uom_id.id,
    #             'price_unit': self.list_price,
    #             'tax_id': [(6, 0, self.taxes_id.ids)],
    #         })