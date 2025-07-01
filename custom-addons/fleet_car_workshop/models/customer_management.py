from odoo import api, fields, models
class Customer(models.Model):
    _name="customer.info"
    _description="Multibrand Car Workshop,biggest workshop of Rajkot"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    cust_name = fields.Char(string="Customer Name",required=True,help="customer info") 
    contact_details = fields.Char(string="Contact Details",required=True)
    cust_type = fields.Selection([('retail','retail'),('corporate','corporate'),('insurance','insurance')],string="Customer Type",required=True)
    insurance_policy_no = fields.Char(string="Insurance Number",required=True)
    vehicle_state = fields.Selection([
    ('AN', 'Andaman and Nicobar Islands'),
    ('AP', 'Andhra Pradesh'),
    ('AR', 'Arunachal Pradesh'),
    ('AS', 'Assam'),
    ('BR', 'Bihar'),
    ('CH', 'Chandigarh'),
    ('CG', 'Chhattisgarh'),
    ('DD', 'Daman and Diu'),
    ('DL', 'Delhi'),
    ('DN', 'Dadra and Nagar Haveli'),
    ('GA', 'Goa'),
    ('GJ', 'Gujarat'),
    ('HR', 'Haryana'),
    ('HP', 'Himachal Pradesh'),
    ('JH', 'Jharkhand'),
    ('JK', 'Jammu and Kashmir'),
    ('KA', 'Karnataka'),
    ('KL', 'Kerala'),
    ('LA', 'Ladakh'),
    ('LD', 'Lakshadweep'),
    ('MH', 'Maharashtra'),
    ('ML', 'Meghalaya'),
    ('MN', 'Manipur'),
    ('MP', 'Madhya Pradesh'),
    ('MZ', 'Mizoram'),
    ('NL', 'Nagaland'),
    ('OD', 'Odisha'),
    ('PB', 'Punjab'),
    ('PY', 'Puducherry'),
    ('RJ', 'Rajasthan'),
    ('SK', 'Sikkim'),
    ('TN', 'Tamil Nadu'),
    ('TS', 'Telangana'),
    ('TR', 'Tripura'),
    ('UP', 'Uttar Pradesh'),
    ('UK', 'Uttarakhand'),
    ('WB', 'West Bengal'),
    ], string="State of Vehicle")
    
    insurance_company_name = fields.Selection([
    ('acko', 'Acko General Insurance'),
    ('bajaj', 'Bajaj Allianz General Insurance'),
    ('bharti', 'Bharti AXA General Insurance'),
    ('chola', 'Cholamandalam MS General Insurance'),
    ('digit', 'Go Digit General Insurance'),
    ('edelweiss', 'Edelweiss General Insurance'),
    ('future', 'Future Generali India Insurance'),
    ('hdfc', 'HDFC ERGO General Insurance'),
    ('icici', 'ICICI Lombard General Insurance'),
    ('iffco', 'IFFCO Tokio General Insurance'),
    ('kotak', 'Kotak Mahindra General Insurance'),
    ('liberty', 'Liberty General Insurance'),
    ('magma', 'Magma HDI General Insurance'),
    ('national', 'National Insurance Company'),
    ('newindia', 'The New India Assurance'),
    ('navi', 'Navi General Insurance'),
    ('oriental', 'The Oriental Insurance Company'),
    ('raheja', 'Raheja QBE General Insurance'),
    ('reliance', 'Reliance General Insurance'),
    ('royal', 'Royal Sundaram General Insurance'),
    ('sbi', 'SBI General Insurance'),
    ('shriram', 'Shriram General Insurance'),
    ('tata', 'TATA AIG General Insurance'),
    ('united', 'United India Insurance Company'),
    ('universal', 'Universal Sompo General Insurance'),
    ], string="Insurance Company Name")
    
    payment_type = fields.Selection([
    ('cash', 'Cash'),
    ('cheque', 'Cheque'),
    ('neft', 'NEFT'),
    ('rtgs', 'RTGS'),
    ('imps', 'IMPS'),
    ('upi', 'UPI'),
    ('credit_card', 'Credit Card'),
    ('debit_card', 'Debit Card'),
    ('net_banking', 'Net Banking'),
    ('wallet', 'Mobile Wallet'),
    ('bank_transfer', 'Bank Transfer'),
    ('emandate', 'E-Mandate'),
    ('dd', 'Demand Draft'),
    ('pos', 'POS Machine'),
    ('others', 'Other'),
    ], string="Preferred Payment Type")
    
    