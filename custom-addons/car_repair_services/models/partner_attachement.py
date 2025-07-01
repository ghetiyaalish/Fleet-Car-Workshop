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


class PartnerAttachment(models.Model):
    _name = 'partner.attachment'
    _description = 'Partner Attachment'

    name = fields.Selection([
        ('insurance_policy', "Insurance Policy"),
        ('rc_front', "RC Front"),
        ('rc_rear', "RC Rear"),
        ('dl_front', "Dl Front"),
        ('dl_rear', "Dl Rear"),
        ('adhar_front', "Adhar Front"),
        ('adhar_rear', "Adhar Rear"),
        ('pan_font', "Pan Card Front"),
        ('bank_detail', "Bank Detail"),
        ('puc', "PUC"),
        ('cng_certificate', "CNG Testing Certificate"),
        ], string="Document Type")
    photo_1920 = fields.Image("Photos", copy=False, attachment=True, max_width=1024, max_height=1024)
    attachment_ids = fields.Binary("Attachment")
    partner_id = fields.Many2one('res.partner', string='Customer Name', required=True)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    partner_id = fields.Many2one('res.partner', string='Customer Name')
    doc_name = fields.Selection([
        ('insurance_policy', "Insurance Policy"),
        ('rc_front', "RC Front"),
        ('rc_rear', "RC Rear"),
        ('dl_front', "Dl Front"),
        ('dl_rear', "Dl Rear"),
        ('adhar_front', "Adhar Front"),
        ('adhar_rear', "Adhar Rear"),
        ('pan_font', "Pan Card Front"),
        ('bank_detail', "Bank Detail"),
        ('puc', "PUC"),
        ('cng_certificate', "CNG Testing Certificate"),
        ], string="Document Type")


    @api.model_create_multi
    def create(self, vals_list):
        results =  super(IrAttachment, self).create(vals_list)
        for res in results:
            if res.partner_id:
                res.res_model = 'res.partner'
                res.res_id = res.partner_id.id
        return results
