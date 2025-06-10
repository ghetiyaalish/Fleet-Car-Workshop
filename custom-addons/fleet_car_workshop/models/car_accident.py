# models/accident_request.py

from odoo import models, fields, api

class AccidentRequest(models.Model):
    _name = "accident.request"
    _description = "Accident repair cars"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'acc_priority desc, acc_request_date desc' # Use new field names in order

    # --- Fields - Added the 'acc_' prefix ---
    acc_name = fields.Char(
        string="Request Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('accident.request') or 'New'
    )

    acc_partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
        required=True,
        tracking=True
    )

    acc_vehicle_details = fields.Char(
        string="Vehicle",
        required=True
    )

    acc_description = fields.Text(
        string="Accident Description"
    )

    acc_request_date = fields.Datetime(
        string="Request Date & Time",
        required=True,
        default=fields.Datetime.now,
        tracking=True
    )

    acc_stage_id = fields.Many2one(
        'accident.request.stage',
        string='Stage',
        required=True,
        tracking=True,
        group_expand='_read_group_stage_ids',
        default=lambda self: self._default_stage_id()
    )

    acc_priority = fields.Selection(
        [
            ('0', 'Low'),
            ('1', 'Normal'),
            ('2', 'High'),
            ('3', 'Very High')
        ],
        default='0',
        index=True,
        tracking=True,
        string="Priority"
    )

    acc_kanban_state = fields.Selection(
        [
            ('normal', 'In Progress'),
            ('done', 'Ready'),
            ('blocked', 'Blocked')
        ],
        string='Kanban State',
        copy=False,
        default='normal',
        required=True,
        tracking=True,
        help="A colored flag indicating the state of the request."
    )

    acc_kanban_state_label = fields.Char(
        compute='_compute_kanban_state_label',
        string='Kanban State Label'
    )

    acc_attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number') # Added for attachments

    # --- Compute Methods - Updated field names ---
    @api.depends('acc_kanban_state') # Depends on new field name
    def _compute_kanban_state_label(self):
        for request in self:
            if request.acc_kanban_state == 'normal': # Uses new field name
                request.acc_kanban_state_label = 'In Progress' # Uses new field name
            elif request.acc_kanban_state == 'done': # Uses new field name
                request.acc_kanban_state_label = 'Ready' # Uses new field name
            else: # blocked
                request.acc_kanban_state_label = 'Blocked' # Uses new field name

    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', self._name), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attachment_by_res_id = {data['res_id']: data['res_id_count'] for data in attachment_data}
        for request in self:
            request.acc_attachment_number = attachment_by_res_id.get(request.id, 0) # Uses new field name


    # --- Default Stage Method - Updated field name ---
    def _default_stage_id(self):
        # Search for stage using the correct stage model and ordering by its new sequence field
        stage = self.env['accident.request.stage'].search([], order='acc_stage_sequence', limit=1)
        return stage.id if stage else False

    # --- Read Group Method - Corrected Signature and field name ---
    @api.model
    def _read_group_stage_ids(self, stages, domain, order): # Corrected signature
        # Search for stages using the correct stage model and ordering by its new sequence field
        return self.env['accident.request.stage'].search([], order='acc_stage_sequence')

    # --- Create Method for Sequence - Updated field name ---
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Generate sequence for the new 'acc_name' field
            if vals.get('acc_name', 'New') == 'New': # Uses new field name
                vals['acc_name'] = self.env['ir.sequence'].next_by_code('accident.request') or 'New'
        return super().create(vals_list)

    # --- Action for Attachments ---
    def action_open_attachments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Attachments',
            'res_model': 'ir.attachment',
            'domain': [('res_model', '=', self._name), ('res_id', '=', self.id)],
            'view_mode': 'kanban,tree,form',
            'help': """
                <p class="o_view_nocontent_smiling_face">
                    Attach files here
                </p>""",
            'limit': 80,
            'context': "{'default_res_model': '%s', 'default_res_id': %d}" % (self._name, self.id)
        }