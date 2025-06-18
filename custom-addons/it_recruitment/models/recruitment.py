from odoo import models, fields, api
class RecruitmentStats(models.Model):
    _name = 'it.recruitment.stats'
    _description = 'Dashboard Stats'
    _auto = False  # This is a SQL view model

    total_applicants = fields.Integer(string='Total Applicants')
    round_1_count = fields.Integer(string='Round 1')
    round_2_count = fields.Integer(string='Round 2')
    round_3_count = fields.Integer(string='Round 3')
    final_count = fields.Integer(string='Final Round')
    hired_count = fields.Integer(string='Hired')
    rejected_count = fields.Integer(string='Rejected')
    pending_count = fields.Integer(string='Pending')
    active_jobs = fields.Integer(string='Active Jobs')
    
    