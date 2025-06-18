from odoo import models, fields, api
class CompanyInfo(models.Model):
    _name = 'it.recruitment.company'
    _description = 'Company Information'

    name = fields.Char(string='Company Name')
    mission = fields.Text(string='Mission')
    vision = fields.Text(string='Vision')
    team_overview = fields.Text(string='Team Overview')
    logo = fields.Binary(string='Company Logo')
