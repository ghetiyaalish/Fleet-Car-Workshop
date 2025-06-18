from odoo import models, fields, api
class Applicant(models.Model):
    _name = 'it.recruitment.applicant'
    _description = 'Job Applicant'
    _order = 'create_date desc'

    name = fields.Char(string='Full Name', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone')
    resume = fields.Binary(string='Resume')
    resume_filename = fields.Char(string="Resume Filename")
    job_id = fields.Many2one('it.recruitment.job', string='Job Applied For', required=True)
    current_round = fields.Selection([
        ('round_1', 'Aptitude Test'),
        ('round_2', 'Coding Round'),
        ('round_3', 'HR Interview'),
        ('final', 'Final Decision')
    ], string='Current Round', default='round_1')
    final_status = fields.Selection([
        ('pending', 'Pending'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected')
    ], string='Final Status', default='pending')
    application_date = fields.Date(string='Application Date', default=fields.Date.today())
    stage_color = fields.Integer(string='Stage Color', compute='_compute_stage_color')
    
    @api.depends('current_round', 'final_status')
    def _compute_stage_color(self):
        for applicant in self:
            if applicant.final_status == 'hired':
                applicant.stage_color = 10  # Green
            elif applicant.final_status == 'rejected':
                applicant.stage_color = 1   # Red
            elif applicant.current_round == 'round_1':
                applicant.stage_color = 2  # Orange
            elif applicant.current_round == 'round_2':
                applicant.stage_color = 3  # Yellow
            elif applicant.current_round == 'round_3':
                applicant.stage_color = 4   # Light blue
            else:
                applicant.stage_color = 5   # Purple
