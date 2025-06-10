# models/accident_request_stage.py

from odoo import models, fields

class AccidentRequestStage(models.Model):
    _name = 'accident.request.stage'
    _description = 'Accident Request Stage'
    _order = 'acc_stage_sequence, acc_stage_name' # Use new field names in order

    # --- Fields - Added the 'acc_stage_' prefix ---
    acc_stage_name = fields.Char(string='Stage Name', required=True, translate=True)
    acc_stage_sequence = fields.Integer(string='Sequence', default=10)
    acc_stage_fold = fields.Boolean(string='Folded in Kanban',
        help='This stage is folded in the Kanban view when there are no records in that stage to display.')