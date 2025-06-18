from odoo import models, fields, api
class JobPosition(models.Model):
    _name = 'it.recruitment.job'
    _description = 'Job Position'
    _order = 'name asc'

    name = fields.Char(string='Job Title', required=True)
    responsibilities = fields.Text(string='Responsibilities')
    requirements = fields.Text(string='Requirements')
    is_active = fields.Boolean(default=True)
    applicant_count = fields.Integer(compute='_compute_applicant_count', string='Applicants')
    
    def _compute_applicant_count(self):
        for job in self:
            job.applicant_count = self.env['it.recruitment.applicant'].search_count([('job_id', '=', job.id)])

