from odoo import api, fields, models
from odoo.exceptions import UserError

class MaterialUsed(models.Model):
    """Model for material used in car workshop"""
    _name = 'material.used'
    _description = 'Material Used in Car Workshop'
    # company_logo = fields.Binary("Company Logo", attachment=True)
    # signature_image = fields.Binary("Authorized Signature", attachment=True)
    

    insurance_company = fields.Many2one(
        'vehicle.details',
        string="Insurance Company",
        required=True,
        help="Select the insurance provider (must be a company)"
    )
    
    policy_no = fields.Char(string="Policy Number",required=True)
    
    claim_no = fields.Char(string="Claim Number" , required=True)
    
    insurance_type = fields.Selection(

    [
        ('0', 'Third Party'),
        ('1', 'Comprehensive'),
        ('2', 'Own Damage')
    ],
    string="Insurance Type",
    required=True
    )
    
    policy_expiry_date = fields.Datetime(string="Policy Date",
        default=fields.Datetime.now,
        tracking=True)
    
    damage_cost = fields.Monetary( string='Damage Price',
        help='Damage Price')
    
    claim_amount = fields.Monetary(string = "Claim Amount" , help="Claim Amount")
        
    car_mo_id = fields.Many2one("vehicle.details",string="Car Brand",required = True)

    license_plate = fields.Char(string="License Plate",help="Registration Number", required=True)
    
    accident_datetime = fields.Datetime(string="Accident Date",required=True)
    
    accident_location = fields.Selection([
    ('gujarat_ahmedabad', 'Gujarat - Ahmedabad'),
    ('gujarat_surat', 'Gujarat - Surat'),
    ('gujarat_vadodara', 'Gujarat - Vadodara'),
    ('gujarat_rajkot', 'Gujarat - Rajkot'),
    ('gujarat_gandhinagar', 'Gujarat - Gandhinagar'),
    ('maharashtra_mumbai', 'Maharashtra - Mumbai'),
    ('maharashtra_pune', 'Maharashtra - Pune'),
    ('maharashtra_nagpur', 'Maharashtra - Nagpur'),
    ('maharashtra_nashik', 'Maharashtra - Nashik'),
    ('maharashtra_thane', 'Maharashtra - Thane'),
    ('karnataka_bengaluru', 'Karnataka - Bengaluru'),
    ('karnataka_mysuru', 'Karnataka - Mysuru'),
    ('karnataka_mangaluru', 'Karnataka - Mangaluru'),
    ('karnataka_hubli', 'Karnataka - Hubli'),
    ('karnataka_belagavi', 'Karnataka - Belagavi'),
    ('tamilnadu_chennai', 'Tamil Nadu - Chennai'),
    ('tamilnadu_coimbatore', 'Tamil Nadu - Coimbatore'),
    ('tamilnadu_madurai', 'Tamil Nadu - Madurai'),
    ('tamilnadu_trichy', 'Tamil Nadu - Tiruchirappalli'),
    ('tamilnadu_salem', 'Tamil Nadu - Salem'),
    ('up_lucknow', 'Uttar Pradesh - Lucknow'),
    ('up_kanpur', 'Uttar Pradesh - Kanpur'),
    ('up_varanasi', 'Uttar Pradesh - Varanasi'),
    ('up_agra', 'Uttar Pradesh - Agra'),
    ('up_meerut', 'Uttar Pradesh - Meerut'),
    ('rajasthan_jaipur', 'Rajasthan - Jaipur'),
    ('rajasthan_jodhpur', 'Rajasthan - Jodhpur'),
    ('rajasthan_kota', 'Rajasthan - Kota'),
    ('rajasthan_udaipur', 'Rajasthan - Udaipur'),
    ('rajasthan_bikaner', 'Rajasthan - Bikaner'),
    ('wb_kolkata', 'West Bengal - Kolkata'),
    ('wb_asansol', 'West Bengal - Asansol'),
    ('wb_siliguri', 'West Bengal - Siliguri'),
    ('wb_durgapur', 'West Bengal - Durgapur'),
    ('wb_howrah', 'West Bengal - Howrah'),
    ('punjab_ludhiana', 'Punjab - Ludhiana'),
    ('punjab_amritsar', 'Punjab - Amritsar'),
    ('punjab_jalandhar', 'Punjab - Jalandhar'),
    ('punjab_patiala', 'Punjab - Patiala'),
    ('punjab_bathinda', 'Punjab - Bathinda'),
    ('mp_bhopal', 'Madhya Pradesh - Bhopal'),
    ('mp_indore', 'Madhya Pradesh - Indore'),
    ('mp_gwalior', 'Madhya Pradesh - Gwalior'),
    ('mp_jabalpur', 'Madhya Pradesh - Jabalpur'),
    ('mp_ujjain', 'Madhya Pradesh - Ujjain'),
    ('bihar_patna', 'Bihar - Patna'),
    ('bihar_gaya', 'Bihar - Gaya'),
    ('bihar_bhagalpur', 'Bihar - Bhagalpur'),
    ('bihar_muzaffarpur', 'Bihar - Muzaffarpur'),
    ('bihar_darbhanga', 'Bihar - Darbhanga'),
    ('telangana_hyderabad', 'Telangana - Hyderabad'),
    ('telangana_warangal', 'Telangana - Warangal'),
    ('telangana_nizamabad', 'Telangana - Nizamabad'),
    ('telangana_karimnagar', 'Telangana - Karimnagar'),
    ('telangana_khammam', 'Telangana - Khammam'),
    ('kerala_thiruvananthapuram', 'Kerala - Thiruvananthapuram'),
    ('kerala_kochi', 'Kerala - Kochi'),
    ('kerala_kozhikode', 'Kerala - Kozhikode'),
    ('kerala_thrissur', 'Kerala - Thrissur'),
    ('kerala_kollam', 'Kerala - Kollam'),
    ('haryana_gurugram', 'Haryana - Gurugram'),
    ('haryana_faridabad', 'Haryana - Faridabad'),
    ('haryana_panipat', 'Haryana - Panipat'),
    ('haryana_rohtak', 'Haryana - Rohtak'),
    ('haryana_ambala', 'Haryana - Ambala'),
    ('odisha_bhubaneswar', 'Odisha - Bhubaneswar'),
    ('odisha_cuttack', 'Odisha - Cuttack'),
    ('odisha_rourkela', 'Odisha - Rourkela'),
    ('odisha_puri', 'Odisha - Puri'),
    ('odisha_sambalpur', 'Odisha - Sambalpur'),
    ('assam_guwahati', 'Assam - Guwahati'),
    ('assam_dibrugarh', 'Assam - Dibrugarh'),
    ('assam_silchar', 'Assam - Silchar'),
    ('assam_jorhat', 'Assam - Jorhat'),
    ('assam_tezpur', 'Assam - Tezpur'),
    ('rajasthan_jaipur', 'Rajasthan - Jaipur'),
    ('rajasthan_jodhpur', 'Rajasthan - Jodhpur'),
    ('rajasthan_kota', 'Rajasthan - Kota'),
    ('rajasthan_udaipur', 'Rajasthan - Udaipur'),
    ('rajasthan_bikaner', 'Rajasthan - Bikaner'),
    ('uttarakhand_dehradun', 'Uttarakhand - Dehradun'),
    ('uttarakhand_haridwar', 'Uttarakhand - Haridwar'),
    ('uttarakhand_nainital', 'Uttarakhand - Nainital'),
    ('uttarakhand_roorkee', 'Uttarakhand - Roorkee'),
    ('uttarakhand_haldwani', 'Uttarakhand - Haldwani'),
    ('hp_shimla', 'Himachal Pradesh - Shimla'),
    ('hp_dharamshala', 'Himachal Pradesh - Dharamshala'),
    ('hp_mandi', 'Himachal Pradesh - Mandi'),
    ('hp_solan', 'Himachal Pradesh - Solan'),
    ('hp_kullu', 'Himachal Pradesh - Kullu'),
    ('cg_raipur', 'Chhattisgarh - Raipur'),
    ('cg_bhilai', 'Chhattisgarh - Bhilai'),
    ('cg_bilaspur', 'Chhattisgarh - Bilaspur'),
    ('cg_durg', 'Chhattisgarh - Durg'),
    ('cg_rajnandgaon', 'Chhattisgarh - Rajnandgaon'),
    ('jk_srinagar', 'Jammu & Kashmir - Srinagar'),
    ('jk_jammu', 'Jammu & Kashmir - Jammu'),
    ('jk_anantnag', 'Jammu & Kashmir - Anantnag'),
    ('jk_baramulla', 'Jammu & Kashmir - Baramulla'),
    ('jk_udhampur', 'Jammu & Kashmir - Udhampur'),
    ('ml_shillong', 'Meghalaya - Shillong'),
    ('ml_tura', 'Meghalaya - Tura'),
    ('ml_nongpoh', 'Meghalaya - Nongpoh'),
    ('ml_jowai', 'Meghalaya - Jowai'),
    ('ml_williamnagar', 'Meghalaya - Williamnagar'),
    ('mn_imphal', 'Manipur - Imphal'),
    ('mn_thoubal', 'Manipur - Thoubal'),
    ('mn_bishnupur', 'Manipur - Bishnupur'),
    ('mn_ukhrul', 'Manipur - Ukhrul'),
    ('mn_churachandpur', 'Manipur - Churachandpur')
    ],string="Accident Loaction",required = True,help="Location")
    
    car_condition = fields.Selection(
        [
        ('0', 'Drivable'),
        ('1', 'Towed'),
        ('2', 'Total Loss')
        ],
        string="Car Condition",
        required=True
    )
    
    insurance_involved = fields.Boolean(string="Insurance Involved",requried=True)
    
    damage_description = fields.Text(string = "Damage Description",required = True)
    
    material_product_id = fields.Many2one(
        'product.product',
        string='Products',
        help="Product used for work"
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        help='The company of material'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Company Currency',
        related='company_id.currency_id',
        readonly=True,
        help='The currency of the company'
    )
    quantity = fields.Integer(
        string='Quantity',
        default=1,
        help='Amount for material used'
    )
    price = fields.Monetary(
        string='Unit Price',
        help='Unit price for material'
    )
    material_id = fields.Many2one(
        'car.workshop',
        help='The work details of material'
    )
    acc_name = fields.Char(
        string="Title",
        required=True,
        tracking=True,
        help='Give Name of the work'
    )
    acc_user_id = fields.Many2one(
        'res.users',
        string='Assigned To',
        default=lambda self: self.env.user,
        tracking=True,
        help='User responsible for the work'
    )
    acc_partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
        tracking=True,
        help='Customer associated with the work'
    )
    acc_tag_ids = fields.Many2many(
        'worksheet.tag',
        string='Tags',
        ondelete='cascade',
        help='Tags for categorizing the work'
    )
    acc_vehicle_details = fields.Char(
        string="Vehicle",
        help='Details of the vehicle being serviced'
    )
    acc_description = fields.Text(
        string="Description",
        help='Detailed description of the work'
    )
    acc_request_date = fields.Datetime(
        string="Request Date & Time",
        default=fields.Datetime.now,
        tracking=True,
        help='When the work was requested'
    )
    acc_stage_id = fields.Many2one(
        'worksheet.stages',
        string='Stage',
        # default=lambda self: self._default_stage_id(),
        # group_expand='_read_group_stage_ids',
        tracking=True,
        index=True,
        ondelete='restrict',
        copy=False,
        help='Current stage of the work'
    )
    acc_priority = fields.Selection(
        [
            ('0', 'Low'),
            ('1', 'Normal'),
            ('2', 'High'),
            ('3', 'Very High')
        ],
        string="Priority",
        default='0',
        tracking=True,
        index=True,
        help='Priority level of the work'
    )
    acc_kanban_state = fields.Selection(
        [
            ('normal', 'In Progress'),
            ('done', 'Ready'),
            ('blocked', 'Delivered')
        ],
        string='Kanban State',
        default='normal',
        required=True,
        tracking=True,
        copy=False,
        help='Kanban state of the task'
    )
    acc_progress = fields.Integer(
        string="Progress (%)",
        compute='_compute_progress',
        store=True,
        help='Completion percentage of the work'
    )

    @api.depends('acc_stage_id')
    def _compute_progress(self):
        """Compute progress based on stage."""
        for record in self:
            # Example: Progress could be mapped from stage sequence
            record.acc_progress = record.acc_stage_id.sequence * 10  # Adjust logic as needed

    @api.onchange('material_product_id')
    def _onchange_material_product_id(self):
        """Update price when product changes."""
        if self.material_product_id:
            self.price = self.material_product_id.lst_price

    def action_low_record(self):
        """Set priority to Low."""
        self.acc_priority = '0'

    def action_normal_record(self):
        """Set priority to Normal."""
        self.acc_priority = '1'

    def action_high_record(self):
        """Set priority to High."""
        self.acc_priority = '2'

    def action_veryhigh_record(self):
        """Set priority to Very High."""
        self.acc_priority = '3'

    # @api.model
    # def _default_stage_id(self):
    #     """Get the default stage (first in sequence)."""
    #     stage = self.env['worksheet.stages'].search([], limit=1, order='sequence asc')
    #     if not stage:
    #         raise UserError("No stages configured. Please create stages first.")
    #     return stage.id

    # @api.model
    # def _read_group_stage_ids(self, stages, domain, order):
    #     """Display all stages in kanban view, even if empty."""
    #     return stages.search([], order=order)
