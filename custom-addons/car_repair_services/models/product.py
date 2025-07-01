# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
#  Part of Dhaval (https://www.upwork.com/freelancers/~01b41453a710f4c7c1).  #
#  See LICENSE file for full copyright and licensing details.                #
#                                                                            #
##############################################################################

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    model_ids = fields.Many2many('car.model', string="Model")
    product_location_id = fields.Many2one('product.location', string="Product Location")
    print_name = fields.Char(string="Print Name")
    pre_inspection_line = fields.One2many('pre.inspection.list', 'product_id', string='Pre Inspection', copy=True, auto_join=True)
    post_inspection_line = fields.One2many('post.inspection.list', 'product_id', string='Post Inspection', copy=True, auto_join=True)
    labour_charge = fields.Char(string="Labour Charge")
    
    
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    product_catalog_product_is_in_job_card = fields.Boolean(
        compute= '_compute_product_is_in_job_card',
        search='_search_product_is_in_job_card',
    )

    # @api.depends_context('job_card_id')
    # def _compute_product_is_in_job_card(self):
    #     job_card_id =self.env.context.get('job_card_id')
    #     if not job_card_id:
    #         self.product_catalog_product_is_in_job_card = False
    #         return
    #     read_group_data = self.env['job.card.line']._read_group(
    #         domain=['job_card_id','=',job_card_id],
    #         groupby=['product_id'],
    #         aggregates=['__count'],
    #     )
    #     data = {product.id:count for product, count in read_group_data}
    #     for product in self:
    #         product.product_catalog_product_is_in_job_card = bool(data.get(product.id,0))
    
class ProductLocation(models.Model):
    _name = 'product.location'
    _description = 'Product Location'

    name = fields.Char(string="Product Location")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Location Name already exist!')
    ]


class InspectionValue(models.Model):
    _name = 'inspection.value'
    _description = 'Inspection Value'

    name = fields.Char(string="Inspection Value", size=15)

    _sql_constraints = [
        ('day_name_uniq', 'unique (name)', 'The Same Name already exist!')
    ]

    # @api.constrains('name')
    # def _check_unique_inspection_name(self):
    #     customer = self.filtered(lambda x: x.name == self.name)
    #     if customer:
    #         raise UserError(_('The Inspection Value already exist!'))


class PreInspection(models.Model):
    _name = 'pre.inspection'
    _description = 'Pre Inspection'

    name = fields.Char(string="Pre Inspection Name")

    _sql_constraints = [
        ('day_name_uniq', 'unique (name)', 'The Same Name already exist!')
    ]


class PreInspectionList(models.Model):
    _name = 'pre.inspection.list'
    _description = 'Pre Inspection List'

    sequence = fields.Integer(string='Sequence', default=1)
    pre_inspection_id = fields.Many2one('pre.inspection', string="Pre Inspection")
    value_id = fields.Many2one('inspection.value', string="Inspection Value")
    product_id = fields.Many2one('product.template', string="Product")


class PostInspection(models.Model):
    _name = 'post.inspection'
    _description = 'Post Inspection'

    name = fields.Char(string="Post Inspection Name")

    _sql_constraints = [
        ('day_name_uniq', 'unique (name)', 'The Same Name already exist!')
    ]


class PostInspectionList(models.Model):
    _name = 'post.inspection.list'
    _description = 'Post Inspection List'

    sequence = fields.Integer(string='Sequence', default=1)
    post_inspection_id = fields.Many2one('post.inspection', string="Post Inspection")
    value_id = fields.Many2one('inspection.value', string="Inspection Value")
    product_id = fields.Many2one('product.template', string="Product")
