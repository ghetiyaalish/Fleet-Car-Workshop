# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
#  Part of Dhaval (https://www.upwork.com/freelancers/~01b41453a710f4c7c1).  #
#  See LICENSE file for full copyright and licensing details.                #
#                                                                            #
##############################################################################

import datetime
import requests

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression


class InsuranceCompany(models.Model):
    _name = 'insurance.company'
    _description = 'insurance Company'

    active = fields.Boolean(default=True, string="Active")
    name = fields.Char(string="Insurance Company Name")


class InsuranceBroker(models.Model):
    _name = 'insurance.broker'
    _description = 'insurance Broker'

    active = fields.Boolean(default=True, string="Active")
    name = fields.Char(string="Insurance Broker Name")


class NotificationDay(models.Model):
    _name = 'notification.day'
    _description = 'Notification Day'

    name = fields.Integer(string="Notification Day")

    _sql_constraints = [
        ('day_name_uniq', 'unique (name)', 'The Notification Day already exist!')
    ]


class PartnerNotification(models.Model):
    _name = 'partner.notification'
    _description = 'notification'

    active = fields.Boolean(default=True, string="Active")
    name = fields.Selection([
        ("insurance_expire", "Insurance Expire"),
        ("puc_expire", "PUC Expire"),
        ("cng_expire", "CNG Expire")], string="Expiry Type", required=True)
    notification_day_ids = fields.Many2many('notification.day', string="Notification Days", required=True)

    _sql_constraints = [
        ('expiry_name_uniq', 'unique (name)', 'The Expiry Type already exist!')
    ]

class InsuranceProvider(models.Model):
    _name = 'insurance.provider'
    _description = 'Insurance Provider'

    name = fields.Char(string="Insurance Provider Name")

    _sql_constraints = [
        ('day_name_uniq', 'unique (name)', 'The Insurance Provider already exist!')
    ]


class InsuranceType(models.Model):
    _name = 'insurance.type'
    _description = 'Insurance Type'

    name = fields.Char(string="Insurance Type")

    _sql_constraints = [
        ('day_name_uniq', 'unique (name)', 'The Insurance Type already exist!')
    ]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_default_country(self):
        country = self.env['res.country'].search([('code', '=', 'IN')], limit=1)
        return country

    @api.model
    def _get_default_state(self):
        state = self.env['res.country.state'].search([('name', '=', 'Gujarat')], limit=1)
        return state

    city = fields.Char(default="Surat")
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]", default=_get_default_state)
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=_get_default_country)

    reg_no = fields.Char(string="Registration No.", size=10)
    model_id = fields.Many2one('car.model', string="Model")
    variant_id = fields.Many2one('car.model.variant', string="Variant")
    make_id = fields.Many2one('car.make', string="Make", readonly=False, related='model_id.make_id')
    color_id = fields.Many2one('car.model.color', string="Color")
    fuel_type = fields.Selection(related="variant_id.fuel_type", readonly=False)
    engine_no = fields.Char(string="Engine No.")
    chassis_no = fields.Char(string="Chassis No.")
    insurance_company = fields.Many2one('insurance.company', string="Insurance Company")
    insurance_broker = fields.Many2one('insurance.broker', string="Insurance Broker")
    insurance_policy_no = fields.Char(string="Insurance Policy No.")
    policy_expiry_date = fields.Date(string="Insurance Exp Date")
    puc_expiry_date = fields.Date(string="PUC Expiry Date")
    cng_expiry_date = fields.Date(string="CNG Testing Expiry Date")
    run_km = fields.Char(string="Run KM./Year")
    new_name = fields.Text(string="Search Name")
    partner_attachment_ids = fields.One2many('partner.attachment', 'partner_id', auto_join=True)
    attachment_ids = fields.One2many('ir.attachment', 'partner_id', auto_join=True)

    pan_no = fields.Char(string="Pan Card No.")
    adhar_no = fields.Char(string="Adhar Card No.")
    birth_date = fields.Date(string="Birth Date")
    contact_type = fields.Selection([
        ('customer','Customer'),
        ('vendor','Vendor'),
        ('insurance','Insurance Company')], default="customer", string='Type')
    job_card_count = fields.Integer(string="Job Card", compute='_get_jobcard')
    total_invoiced_due = fields.Monetary(compute='_invoice_due_total', string="Outstanding")
    claim = fields.Selection([
        ('yes','Yes'),
        ('no','No')], default="no", string='Claim')
    insurance_type_ids = fields.Many2many('insurance.type', string="Insurance Type")
    insurance_provider_ids = fields.Many2many('insurance.provider', string="Insurance Provider")

    @api.depends('total_invoiced')
    def _invoice_due_total(self):
        for partner in self:
            invoiceRec = self.env['account.move'].sudo().search([
                ('move_type', '=', 'out_invoice'),
                ('partner_id', '=', partner.id),
                ('state', '=', 'posted')])
            partner.total_invoiced_due = sum(invoiceRec.mapped('amount_residual_signed'))

    def _get_jobcard(self):
        for rec in self:
            jobCardIds = self.env['job.card'].search_count([('partner_id','=',rec.id)])
            rec.job_card_count = jobCardIds

    def action_view_jobcard(self):
        jobCardIds = self.env['job.card'].search([('partner_id','=',self.id)])
        action = self.env["ir.actions.actions"]._for_xml_id("car_repair_services.action_job_card")
        if len(jobCardIds) > 1:
            action['domain'] = [('id', 'in', jobCardIds.ids)]
        elif len(jobCardIds) == 1:
            form_view = [(self.env.ref('car_repair_services.job_card_form_view').id, 'form')]
            action['views'] = form_view
            action['res_id'] = jobCardIds.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.onchange('company_type')
    def onchange_company_type(self):
        res = super().onchange_company_type()
        if self.country_id and self.country_id.code == 'IN':
            self.l10n_in_gst_treatment = 'unregistered'
        return res

    @api.onchange('country_id')
    def _onchange_country_id(self):
        res = super()._onchange_country_id()
        if self.country_id and self.country_id.code != 'IN':
            self.l10n_in_gst_treatment = 'overseas'
        elif self.country_id and self.country_id.code == 'IN':
            self.l10n_in_gst_treatment = 'unregistered'
        return res

    @api.constrains('reg_no')
    def _check_unique_registration(self):
        for customer in self.search([('reg_no','=',self.reg_no),
            ('id','!=',self.id),('contact_type','=','customer')]):
            print("customer===========",customer.name,customer.id)
            if customer:
                raise UserError(_('The Registration number already exist!'))

    @api.model_create_multi
    def create(self, vals):
        result = super(ResPartner, self).create(vals)
        if result and result.reg_no:
            result.reg_no = result.reg_no.upper()
        if result and result.name:
            result.name = result.name.upper()
        result.display_name = result.name
        # result.new_name = result.name + result.reg_no + result.model_id.name
        return result

    def write(self, vals):
        result = super(ResPartner, self).write(vals)
        if vals.get('name'):
            self.display_name = vals.get('name') 
        return result

    @api.onchange('name', 'reg_no', 'model_id')
    def _onchange_new_name(self):
        newName = ''
        self.new_name = ''
        if self.name:
            newName += self.name
        if self.reg_no:
            self.reg_no = self.reg_no.upper()
            newName += ' ['+ self.reg_no +'] '
        if self.model_id:
            newName += '['+ self.model_id.name +']'
        self.new_name = newName

    # def name_get(self):
    #     res = []
    #     for result in self:
    #         if result.name and result.reg_no and result.model_id:
    #             # if order.partner_id.name:
    #             #     name = '%s - %s' % (name, order.partner_id.name)
    #             res.append((result.id, result.name.ljust(30, '.') + result.reg_no.ljust(15, '.') + result.model_id.name))
    #     return res
    #     # return super(SaleOrder, self).name_get()

    def name_get(self):
        """ Display 'Warehouse_name: PickingType_name' """
        res = []
        for partner in self:
            if partner.name and partner.reg_no and partner.model_id:
                name = partner.name + ' [' + partner.reg_no + '] ' + '[' + partner.model_id.name + ']'
            else:
                name = partner.name
            res.append((partner.id, name))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None,order=None):
        args = args or []
        domain = []
        if name:
            # # Try to reverse the `name_get` structure
            # parts = name.split(': ')
            # if len(parts) == 2:
            #     domain = [('warehouse_id.name', operator, parts[0]), ('name', operator, parts[1])]
            # else:
            domain = ['|', ('name', operator, name), ('new_name', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid,order=order)

    @api.model
    def _autosend_insurance_expiry_whatsapp_notification(self):
        ''' This method is called from a cron job.
        It is used to send whatsapp notification for insurance expiry.
        '''
        insuranceExpire = self.env['partner.notification'].search([('name', '=', 'insurance_expire'),('active','=', True)], limit=1)
        for day in insuranceExpire.notification_day_ids:
            expiryDate = datetime.date.today() + datetime.timedelta(day.name)
            whatsappURL = self.env['ir.config_parameter'].sudo().get_param('car_repair_services.whatsapp_url')
            whatsappInstance = self.env['ir.config_parameter'].sudo().get_param('car_repair_services.whatsapp_instance')
            whatsappToken = self.env['ir.config_parameter'].sudo().get_param('car_repair_services.whatsapp_token')
            records = self.search([('policy_expiry_date', '=', expiryDate)])
            for customer in records:
                messageText = "Hello %s,\n\nYour car Insurance policy expire soon.\n\nPlease contact us.\n(Yash Motors)\n\n\nThank you"%(customer.name)
                url = "%snumber=%s&type=text&message=%s&instance_id=%s&access_token=%s"%(
                    whatsappURL,
                    customer.mobile.replace(" ", '').replace('+', ''),
                    messageText,
                    whatsappInstance,
                    whatsappToken)
                response = requests.get(url)
                customer.message_post(body=_("Whatsapp - Message Sent:" + messageText))
