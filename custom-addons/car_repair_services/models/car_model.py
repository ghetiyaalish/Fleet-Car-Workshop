# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
#  Part of Dhaval (https://www.upwork.com/freelancers/~01b41453a710f4c7c1).  #
#  See LICENSE file for full copyright and licensing details.                #
#                                                                            #
##############################################################################

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError

import base64


class CarMake(models.Model):
    _name = 'car.make'
    _description = 'Make'
    _order = 'name asc'

    active = fields.Boolean(default=True, string="Active")
    name = fields.Char(string="Make")
    image_128 = fields.Image("Logo", max_width=128, max_height=128)


class CarModel(models.Model):
    _name = 'car.model'
    _description = 'Model'

    active = fields.Boolean(default=True, string="Active")
    make_id = fields.Many2one('car.make', string="Make")
    name = fields.Char(string="Model Name")


class CarModelColor(models.Model):
    _name = 'car.model.color'
    _description = 'Model Color'

    active = fields.Boolean(default=True, string="Active")
    name = fields.Char(string="Color")


class CarModelVariant(models.Model):
    _name = 'car.model.variant'
    _description = 'Model Variant'

    active = fields.Boolean(default=True, string="Active")
    name = fields.Char(string="Model Name")
    model_id = fields.Many2one('car.model', string="Model")
    make_id = fields.Many2one(related='model_id.make_id', string="Make", readonly=False)
    fuel_type = fields.Selection([("petrol", "Petrol"),("diesel", "Diesel"),("cng", "CNG"),("electric", "Electric")])
