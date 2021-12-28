# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, Warning
import logging

_logger = logging.getLogger(__name__)


class ResRenewal(models.Model):
    _name = 'res.renewal'
    _description = 'Renovaciones'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(string=u'Número', required=False, readonly=True)
    partner_id = fields.Many2one('res.partner', string='Cliente', required=True)
    to_expire = fields.Boolean(string=u'Próxima a expirar', default=False, readonly=False)
    state = fields.Selection(selection=[
        ('draft', 'Borrador'),
        ('process', 'Vigente'),
        ('expired', 'Vencido'),
        ('cancel', 'Cancelado')], string='Estado', required=True, readonly=True, default='draft')

    partner_sequence = fields.Char(related='partner_id.partner_sequence')
    type = fields.Selection(related='partner_id.type')
    is_company = fields.Boolean(related='partner_id.is_company')
    street = fields.Char(related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2')
    city = fields.Char(string='Ciudad', related='partner_id.city')
    state_id = fields.Many2one(string='Estado', related='partner_id.state_id')
    zip = fields.Char(string='C.P.', related='partner_id.zip')
    country_id = fields.Many2one(string=u'País', related='partner_id.country_id')
    vat = fields.Char(string='RFC', related='partner_id.vat')
    parent_id = fields.Many2one(string=u'Compañía', related='partner_id.parent_id')
    company_name = fields.Char(string=u'Nombre Compañía', related='partner_id.company_name')

    function = fields.Char(string='Puesto de trabajo', related='partner_id.function')
    phone = fields.Char(string=u'Teléfono', related='partner_id.phone')
    mobile = fields.Char(string='Celular', related='partner_id.mobile')
    email = fields.Char(string='Email', related='partner_id.email')
    website = fields.Char(string='Sitio Web', related='partner_id.website')
    title = fields.Many2one(string=u'Título', related='partner_id.title')
    category_id = fields.Many2many(string=u'Categorías', related='partner_id.category_id')
    # ------------------------------------------------------
    purchase_licenses = fields.Boolean('Compra de licencias', related='partner_id.purchase_licenses', readonly=False)
    system_implementation = fields.Boolean('Implementación de sistemas', related='partner_id.system_implementation', readonly=False)
    system_customization = fields.Boolean('Personalización de sistemas', related='partner_id.system_customization', readonly=False)
    training = fields.Boolean('Capacitación', related='partner_id.training', readonly=False)
    hardware_software = fields.Boolean('Hardware o Software', related='partner_id.hardware_software', readonly=False)
    have_systems_area = fields.Boolean('Cuentan con area de sistemas', related='partner_id.have_systems_area', readonly=False)
    computers_in_network = fields.Integer('Cuantos equipo hay en su red', related='partner_id.computers_in_network', readonly=False)
    description_aesa = fields.Text(u'Descripción', related='partner_id.description_aesa', readonly=False)
    description_crm = fields.Text('Notas internas', related='partner_id.description_crm', readonly=False)
    personality = fields.Selection('Personalidad del cliente', related='partner_id.personality', readonly=False)
    necessity = fields.Selection('Necesidad', related='partner_id.necessity', readonly=False)
    impact = fields.Selection('Impacto', related='partner_id.impact', readonly=False)
    time = fields.Selection('Tiempo', related='partner_id.time', readonly=False)
    authority = fields.Selection('Autoridad', related='partner_id.authority', readonly=False)
    has_server = fields.Selection('Cuentan con servidor', related='partner_id.has_server', readonly=False)
    server_type = fields.Selection('Tipo de servidor', related='partner_id.server_type', readonly=False)
    own_server = fields.Selection('Servidor propio', related='partner_id.own_server', readonly=False)
    cut_date = fields.Date('Fecha de corte', related='partner_id.cut_date', readonly=False)
    ip_server = fields.Char(u'Dirección IP', related='partner_id.ip_server', readonly=False)
    url_server = fields.Char('OP Activa (URL)', related='partner_id.url_server', readonly=False)
    recurring_customer = fields.Selection('Cliente recurrente de timbres', related='partner_id.recurring_customer', readonly=False)
    number_rings = fields.Selection('Número de timbres', related='partner_id.number_rings', readonly=False)
    last_sale = fields.Date('Fecha de última venta', related='partner_id.last_sale', readonly=False)

    aspel_systems = fields.One2many(related='partner_id.aspel_systems', readonly=False)
    aspel_system_id = fields.Many2one('aspel.system', string='Sistema')
    user_numbers = fields.Selection(related='aspel_system_id.user_numbers')
    serial_number_aesa = fields.Char(related='aspel_system_id.serial_number_aesa')
    version = fields.Char('Versión', related='aspel_system_id.version')
    type_id = fields.Many2one(related='aspel_system_id.type_id', string='Tipo')
    new_date = fields.Date('Fecha renovación', related='aspel_system_id.new_date')
    source_id = fields.Many2one(related='partner_id.source_id', readonly=False)
    history_comments = fields.Text(related='partner_id.aesa_comments', readonly=False)

    DAYS_TO_EXPIRE = 7

    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).\
                next_by_code('sequence.res.renewal')
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('sequence.res.renewal')
        result = super(ResRenewal, self).create(vals)
        return result

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_process(self):
        self.write({'state': 'process'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_expired(self):
        self.write({'state': 'expired'})

    def action_to_expire(self):
        self.write({'to_expire': True})

    def action_renew(self):
        value = self.aspel_system_id.type_id.value
        sys_type = self.aspel_system_id.type_id.value_type
        days = months = years = 0
        if sys_type == 'dias':
            days = value
        elif sys_type == 'meses':
            months = value
        elif sys_type == 'bimestres':
            months = value * 2
        elif sys_type == 'trimestres':
            months = value * 3
        elif sys_type == 'year':
            years = value
        date_sys = self.aspel_system_id.new_date
        date_renew = date_sys + relativedelta(years=years, months=months, days=days)
        if date_renew != date_sys:
            self.aspel_system_id.write({'new_date': date_renew})
        renew_data = {'to_expire': False}
        if self.state != 'process':
            renew_data.update({'state': 'process'})
        self.write(renew_data)
        _logger.info(f"::::: Sistema con folio [{self.name}] renovado correctamente hasta {date_renew}! :::::")

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.aspel_system_id = False

    def action_renovations_to_expire(self):
        _logger.info("::::: Planificador de Renovaciones a vencer ejecutado! :::::")
        days = int(self.DAYS_TO_EXPIRE)
        date_exp = (datetime.now() + timedelta(days=days)).date()
        domain = [('new_date', '<=', date_exp),
                  ('state', '=', 'process')
                  ]
        ren_ids = self.search(domain)
        for ren in ren_ids:
            ren.action_to_expire()

    def schedule_renovations(self):
        _logger.info("::::: Starting Renovations schedule :::::")
        self.action_renovations_to_expire()
        dominio = [('new_date', '<', date.today()),
                   ('state', '=', 'process'),
                   ]
        renov_ids = self.search(dominio)
        for ren in renov_ids:
            ren.action_expired()
        _logger.info("::::: Finished Renovations schedule :::::")

    @api.model
    def _action_renew_batch(self):
        _logger.info("::::: Starting Renovations Batch :::::")
        count = 0
        orders = self.env['res.renewal'].browse(self._context.get('active_ids', []))
        for record in orders:
            record.action_renew()
            count += 1
        self.env.cr.commit()
        _logger.info("::::: Finished Renovations Batch :::::")
        return count

    @api.model
    def _action_renew_batch_result(self):
        """ Separados el update value en db del mensaje al Usuario pq el Warning no deja escribir
            en la base de datos detenindo la acción write() del metodo.
        @return:
        """
        renewed = self._action_renew_batch()
        message = _('Proceso finalizado correctamente! Renovado(s) %i registro(s)' % renewed)
        raise Warning(message)
