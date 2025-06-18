from odoo import models, fields, api
class ContactInquiry(models.Model):
    _name = 'it.recruitment.inquiry'
    _description = 'Contact Inquiry'

    name = fields.Char(string='Name')
    email = fields.Char(string='Email')
    message = fields.Text(string='Message')
    phone = fields.Char(string='Phone')
    address = fields.Text(string='Address')
    map_url = fields.Char(string='Google Map URL')