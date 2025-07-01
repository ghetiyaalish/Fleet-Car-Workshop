# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
#  Part of Dhaval (https://www.upwork.com/freelancers/~01b41453a710f4c7c1).  #
#  See LICENSE file for full copyright and licensing details.                #
#                                                                            #
##############################################################################

from odoo import api, models, fields, _
from odoo.tools.misc import formatLang, format_date, get_lang, groupby
from collections import defaultdict
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta
from collections import defaultdict
from contextlib import contextmanager
from itertools import zip_longest
from hashlib import sha256
from json import dumps
from unittest.mock import patch

import ast
import json
import re
import warnings


class AccountMove(models.Model):
    _inherit = 'account.move'

    reg_no = fields.Char(string="Registration No.", related="partner_id.reg_no", depends=['partner_id.reg_no'], store=True)
    make_id = fields.Many2one(string="Make", related="partner_id.make_id", depends=['partner_id.make_id'], store=True)
    model_id = fields.Many2one(string="Model", related="partner_id.model_id", depends=['partner_id.model_id'], store=True)
    job_card_id = fields.Many2one('job.card', string='Job Card')
    run_km = fields.Char(string="Odometer(KM)", related="job_card_id.run_km", depends=['job_card_id.run_km'], store=True)
    insurance_company_id = fields.Many2one('res.partner', string='Insurance Company', domain="[('contact_type', '=', 'insurance')]")

    def _prepare_tax_lines_data_for_totals_from_object(self, object_lines, tax_results_function):
        tax_lines_data = []

        for line in object_lines:
            tax_results = tax_results_function(line)

            for tax_result in tax_results['taxes']:
                current_tax = self.env['account.tax'].browse(tax_result['id'])

                # Tax line
                tax_lines_data.append({
                    'line_key': f"tax_line_{line.id}_{tax_result['id']}",
                    'tax_amount': tax_result['amount'],
                    'tax': current_tax,
                })

                # Base for this tax line
                tax_lines_data.append({
                    'line_key': 'base_line_%s' % line.id,
                    'base_amount': tax_results['total_excluded'],
                    'tax': current_tax,
                })

                # Base for the taxes whose base is affected by this tax line
                if tax_result['tax_ids']:
                    affected_taxes = self.env['account.tax'].browse(tax_result['tax_ids'])
                    for affected_tax in affected_taxes:
                        tax_lines_data.append({
                            'line_key': 'affecting_base_line_%s_%s' % (line.id, tax_result['id']),
                            'base_amount': tax_result['amount'],
                            'tax': affected_tax,
                            'tax_affecting_base': current_tax,
                        })

        return tax_lines_data

    def _get_tax_totals(self, partner, tax_lines_data, amount_total, amount_untaxed, currency):
        account_tax = self.env['account.tax']

        grouped_taxes = defaultdict(lambda: defaultdict(lambda: {'base_amount': 0.0, 'tax_amount': 0.0, 'base_line_keys': set()}))
        subtotal_priorities = {}
        for line_data in tax_lines_data:
            tax_group = line_data['tax'].tax_group_id

            # Update subtotals priorities
            if tax_group.preceding_subtotal:
                subtotal_title = tax_group.preceding_subtotal
                new_priority = tax_group.sequence
            else:
                # When needed, the default subtotal is always the most prioritary
                subtotal_title = _("Untaxed Amount")
                new_priority = 0

            if subtotal_title not in subtotal_priorities or new_priority < subtotal_priorities[subtotal_title]:
                subtotal_priorities[subtotal_title] = new_priority

            # Update tax data
            tax_group_vals = grouped_taxes[subtotal_title][tax_group]

            if 'base_amount' in line_data:
                # Base line
                if tax_group == line_data.get('tax_affecting_base', account_tax).tax_group_id:
                    # In case the base has a tax_line_id belonging to the same group as the base tax,
                    # the base for the group will be computed by the base tax's original line (the one with tax_ids and no tax_line_id)
                    continue

                if line_data['line_key'] not in tax_group_vals['base_line_keys']:
                    # If the base line hasn't been taken into account yet, at its amount to the base total.
                    tax_group_vals['base_line_keys'].add(line_data['line_key'])
                    tax_group_vals['base_amount'] += line_data['base_amount']

            else:
                # Tax line
                tax_group_vals['tax_amount'] += line_data['tax_amount']

        # Compute groups_by_subtotal
        groups_by_subtotal = {}
        for subtotal_title, groups in grouped_taxes.items():
            groups_vals = [{
                'tax_group_name': group.name,
                'tax_group_amount': amounts['tax_amount'],
                'tax_group_base_amount': amounts['base_amount'],
                'formatted_tax_group_amount': formatLang(self.env, amounts['tax_amount'], currency_obj=currency),
                'formatted_tax_group_base_amount': formatLang(self.env, amounts['base_amount'], currency_obj=currency),
                'tax_group_id': group.id,
                'group_key': '%s-%s' %(subtotal_title, group.id),
            } for group, amounts in sorted(groups.items(), key=lambda l: l[0].sequence)]

            groups_by_subtotal[subtotal_title] = groups_vals

        # Compute subtotals
        subtotals_list = [] # List, so that we preserve their order
        previous_subtotals_tax_amount = 0
        for subtotal_title in sorted((sub for sub in subtotal_priorities), key=lambda x: subtotal_priorities[x]):
            subtotal_value = amount_untaxed + previous_subtotals_tax_amount
            subtotals_list.append({
                'name': subtotal_title,
                'amount': subtotal_value,
                'formatted_amount': formatLang(self.env, subtotal_value, currency_obj=currency),
            })

            subtotal_tax_amount = sum(group_val['tax_group_amount'] for group_val in groups_by_subtotal[subtotal_title])
            previous_subtotals_tax_amount += subtotal_tax_amount
        
        # Assign json-formatted result to the field
        return {
            'amount_total': amount_total,
            'amount_untaxed': amount_untaxed,
            'formatted_amount_total': formatLang(self.env, amount_total, currency_obj=currency),
            'formatted_amount_untaxed': formatLang(self.env, amount_untaxed, currency_obj=currency),
            'groups_by_subtotal': groups_by_subtotal,
            'subtotals': subtotals_list,
            'allow_tax_edition': False,
        }


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

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

    approval = fields.Selection([('yes', 'Yes'),('no', 'No')], string='Approval')
    categ_id = fields.Many2one('product.category', string='Categories', change_default=True, ondelete='restrict')
    model_id = fields.Many2one(string="Model", related="move_id.partner_id.model_id", depends=['move_id.partner_id.model_id'], store=True)
    product_ids = fields.Many2many('product.product', string='Product', compute="_compute_prroduct_ids")
