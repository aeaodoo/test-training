# -*- coding: utf-8 -*-
from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def get_default_lead_sequence(self):
        sequence = self.env['ir.sequence'].search(
            [('code','=','sequence.lead')]
            )
        next = sequence.get_next_char(sequence.number_next_actual)

        return next

    def get_default_opportunity_sequence(self):
        sequence = self.env['ir.sequence'].search(
            [('code','=','sequence.opportunity')]
        )
        next = sequence.get_next_char(sequence.number_next_actual)

        return next

    # ESTE METODO GENERA ERROR DE INSTALACION/ACTUALIZACION
    # def planned_revenue(self):
    #     pass

    def _compute_planned_revenue_aesa(self):
        total = 0
        for lead in self:
            total = 0
            for order in lead.order_ids:
                if order.state in ('draft', 'sent'):
                    total += order.amount_untaxed
            lead.planned_revenue_aesa = total

    lead_sequence = fields.Char(
        string="Iniciativa",
        size=24,
        readonly=True
    )
    opportunity_sequence = fields.Char(
        string="Oportunidad",
        size=24,
        readonly=True
    )

    purchase_licenses = fields.Boolean('Compra de licencias')
    system_implementation = fields.Boolean('Implementación de sistemas')
    system_customization = fields.Boolean('Personalización de sistemas')
    training = fields.Boolean('Capacitación')
    hardware_software = fields.Boolean('Hardware o Software')
    have_systems_area = fields.Boolean('Cuentan con area de sistemas')
    computers_in_network = fields.Integer('Cuantos equipo hay en su red')
    description_aesa = fields.Text('Descripción')
    personality = fields.Selection(
        [
            ('amarillo', 'Amarillo'),
            ('verde', 'Verde'),
            ('azul', 'Azul'),
            ('Rojo', 'Rojo'),
        ],
        'Personalidad del cliente'
    )
    necessity = fields.Selection([
        ('25_1', 'Compra de licencias'),
        ('25_2', 'Suscripción'),
        ('25_3', 'Timbres'),
        ('25_4', 'Implementación de sistemas'),
        ('25_5', 'Personalización de sistemas'),
        ('25_6', 'Capacitación'),
        ('25_7', 'Software y Hardware'),
    ], 'Necesidad')
    impact = fields.Selection([
        ('5', 'Bajo'),
        ('15', 'Medio'),
        ('25', 'Alto'),
    ], 'Impacto')
    time = fields.Selection([
        ('25', 'Inmediato'),
        ('17', '1 Semana'),
        ('12', '2 Semanas'),
        ('7', 'Tiempo indefinido'),
    ], 'Tiempo')
    authority = fields.Selection([
        ('24.99', 'Contacto principal'),
        ('17', 'Jefe inmediato'),
        ('12', 'Director'),
        ('7', 'Consejo'),
    ], 'Autoridad')

    has_server = fields.Selection(
        [('0', 'Sin servidor'),('1', 'Servidor propio')],
        'Cuentan con servidor'
    )
    server_type = fields.Selection(
        [
            ('local', 'Servidor local'),
            ('cloud', 'Propio cloud'),
        ],
        'Tipo de servidor'
    )
    own_server = fields.Selection(
        [
            ('cloud_aesa', 'Cloud AESA'),
            ('cloud_basico', 'Cloud básico'),
            ('cloud_estandar', 'Cloud Server estándar'),
            ('cloud_premium', 'Cloud Server premium'),
            ('cloud_flex', 'Cloud Server flex'),
            ('cloud_l', 'Cloud Server L'),
            ('cloud_xl', 'Cloud Server XL'),
            ('cloud_xxl', 'Cloud Server XXL'),
            ('cloud_xxxl', 'Cloud Server XXXL'),
            ('cloud_dedicado', 'Cloud Server dedicado'),
        ],
        'Servidor propio'
    )
    cut_date = fields.Date('Fecha de corte')
    ip_server = fields.Char('Dirección IP')
    url_server = fields.Char('OP Activa (URL)')
    recurring_customer = fields.Selection(
        [('0', 'No'),('1', 'Si')], 'Cliente recurrente de timbres'
    )
    number_rings = fields.Selection(
        [('50','50'),
        ('200','200'),
        ('400','400'),
        ('1000','1000'),
        ('2000','2000'),
        ('5000','5000'),
        ('10000','10000'),
        ('20000','20000'),
        ('50000','50000'),
        ('70000','70000'),
        ('100000','100000')],
        'Número de timbres'
    )
    last_sale = fields.Date('Fecha de última venta')
    aspel_systems = fields.One2many(
        'aspel.system',
        'lead_id'
    )
    planned_revenue_aesa = fields.Float('Ingreso estimado', digits=(8,2), compute='_compute_planned_revenue_aesa')
    aesa_comments = fields.Text('Comentarios')

    @api.onchange('necessity', 'impact', 'time', 'authority')
    def on_change_probability_values(self):
        sum = 0
        if(self.necessity):
            sum += float(self.necessity.split('_')[0])
        if(self.impact):
            sum += float(self.impact)
        if(self.time):
            sum += float(self.time)
        if(self.authority):
            sum += float(self.authority)

        self.probability = sum

    @api.model
    def create(self, vals):
        vals['opportunity_sequence'] = \
        self.env['ir.sequence'].next_by_code('sequence.opportunity')
        vals['lead_sequence'] = \
        self.env['ir.sequence'].next_by_code('sequence.lead')
        rec = super(CrmLead, self).create(vals)
        return rec


    def _create_lead_partner_data(self, name, is_company, parent_id=False):
        res = super(CrmLead, self)._create_lead_partner_data(
            name, is_company, parent_id
        )

        res['purchase_licenses'] = self.purchase_licenses
        res['system_implementation'] = self.system_implementation
        res['system_customization'] = self.system_customization
        res['training'] = self.training
        res['hardware_software'] = self.hardware_software
        res['have_systems_area'] = self.have_systems_area
        res['computers_in_network'] = self.computers_in_network
        res['description_aesa'] = self.description_aesa
        res['personality'] = self.personality
        res['necessity'] = self.necessity
        res['impact'] = self.impact
        res['time'] = self.time
        res['authority'] = self.authority
        res['has_server'] = self.has_server
        res['server_type'] = self.server_type
        res['cut_date'] = self.cut_date
        res['ip_server'] = self.ip_server
        res['url_server'] = self.url_server
        res['recurring_customer'] = self.recurring_customer
        res['number_rings'] = self.number_rings
        res['last_sale'] = self.last_sale
        res['description_crm'] = self.description
        res['own_server'] = self.own_server
        res['aesa_comments'] = self.aesa_comments
        if(self.source_id):
            res['source_id'] = self.source_id.id

        aspel_lines = []

        for line in self.aspel_systems:
            aspel_lines.append((0, 0, {
                'aspel_id': line.aspel_id.id,
                'user_numbers': line.user_numbers,
                'serial_number_aesa': line.serial_number_aesa,
                'type_id': line.type_id.id,
                'version': line.version,
                'new_date': line.new_date,
            }))

        res['aspel_systems'] = aspel_lines
        return res
