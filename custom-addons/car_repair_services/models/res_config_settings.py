
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    whatsapp_url = fields.Char('Whatsapp URL')
    whatsapp_instance = fields.Char('Whatsapp Instance')
    whatsapp_token = fields.Char('Whatsapp Token')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        Param = self.env['ir.config_parameter'].sudo()
        res['whatsapp_url'] = Param.sudo().get_param('car_repair_services.whatsapp_url')
        res['whatsapp_instance'] = Param.sudo().get_param('car_repair_services.whatsapp_instance')
        res['whatsapp_token'] = Param.sudo().get_param('car_repair_services.whatsapp_token')
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('car_repair_services.whatsapp_url', self.whatsapp_url)
        self.env['ir.config_parameter'].sudo().set_param('car_repair_services.whatsapp_instance', self.whatsapp_instance)
        self.env['ir.config_parameter'].sudo().set_param('car_repair_services.whatsapp_token', self.whatsapp_token)
