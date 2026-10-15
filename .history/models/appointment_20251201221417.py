# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class Appointment(models.Model):
    _name = 'clinic.appointment'
    _description = 'Rendez-vous Médical'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'appointment_date desc, appointment_time desc'
    _rec_name = 'reference'
    
    # Référence unique
    reference = fields.Char(string='Référence', required=True, copy=False, 
                           readonly=True, default='Nouveau', index=True)
    
    # Patient et Médecin
    patient_id = fields.Many2one('clinic.patient', string='Patient', 
                                required=True, tracking=True, index=True)
    doctor_id = fields.Many2one('clinic.doctor', string='Médecin', 
                               required=True, tracking=True, index=True)
    
    # Date et Heure
    appointment_date = fields.Date(string='Date du RDV', required=True, 
                                   default=fields.Date.today, tracking=True, index=True)
    appointment_time = fields.Float(string='Heure', required=True, tracking=True,
                                   help='Format 24h: 9.0 = 09:00, 14.5 = 14:30')
    
    # Heure affichée (calculée)
    display_time = fields.Char(string='Heure', compute='_compute_display_time', 
                              store=True, readonly=True)
    
    # Datetime combiné pour calendrier
    appointment_datetime = fields.Datetime(string='Date/Heure', 
                                          compute='_compute_datetime', 
                                          store=True, readonly=True)
    
    # État du rendez-vous
    state = fields.Selection([
        ('waiting', 'En Attente'),
        ('with_doctor', 'Chez le Médecin'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé')
    ], string='État', default='waiting', required=True, tracking=True)
    
    # Priorité (URGENT en ROUGE)
    priority = fields.Selection([
        ('normal', 'Normal'),
        ('urgent', 'Urgent')
    ], string='Priorité', default='normal', required=True, tracking=True)
    
    # Motif et notes
    reason = fields.Text(string='Motif du Rendez-vous')
    notes = fields.Text(string='Notes de la Réception')
    
    # Relation avec consultation
    consultation_id = fields.Many2one('clinic.consultation', string='Consultation', 
                                     readonly=True, copy=False)
    
    # Champs relationnels pour affichage
    patient_phone = fields.Char(related='patient_id.phone', string='Tél. Patient', readonly=True)
    patient_email = fields.Char(related='patient_id.email', string='Email Patient', readonly=True)
    patient_age = fields.Integer(related='patient_id.age', string='Âge', readonly=True)
    doctor_specialization = fields.Char(related='doctor_id.specialization', 
                                       string='Spécialité', readonly=True)
    
    # Email envoyé
    email_sent = fields.Boolean(string='Email Envoyé', default=False, copy=False, tracking=True)
    email_sent_date = fields.Datetime(string='Date Envoi Email', readonly=True, copy=False)
    
    # Couleur pour affichage (urgent = rouge)
    color = fields.Integer(string='Couleur', compute='_compute_color', store=True)
    
    # Active
    active = fields.Boolean(string='Actif', default=True)
    
    @api.model
    def create(self, vals):
        """Générer référence unique et envoyer email"""
        if vals.get('reference', 'Nouveau') == 'Nouveau':
            vals['reference'] = self.env['ir.sequence'].next_by_code('clinic.appointment') or 'RDV-NEW'
        
        appointment = super(Appointment, self).create(vals)
        
        # Envoyer email de confirmation pour RDV futurs
        if appointment.appointment_date >= fields.Date.today():
            appointment.send_confirmation_email()
        
        return appointment
    
    @api.depends('appointment_time')
    def _compute_display_time(self):
        """Convertir heure décimale en format HH:MM"""
        for record in self:
            if record.appointment_time:
                hours = int(record.appointment_time)
                minutes = int((record.appointment_time - hours) * 60)
                record.display_time = f"{hours:02d}:{minutes:02d}"
            else:
                record.display_time = "00:00"
    
    @api.depends('appointment_date', 'appointment_time')
    def _compute_datetime(self):
        """Créer datetime pour calendrier"""
        for record in self:
            if record.appointment_date and record.appointment_time:
                hours = int(record.appointment_time)
                minutes = int((record.appointment_time - hours) * 60)
                record.appointment_datetime = datetime.combine(
                    record.appointment_date,
                    datetime.min.time().replace(hour=hours, minute=minutes)
                )
            else:
                record.appointment_datetime = False
    
    @api.depends('priority', 'state')
    def _compute_color(self):
        """Couleur selon priorité et état"""
        for record in self:
            if record.state == 'cancelled':
                record.color = 1  # Rouge grisé
            elif record.priority == 'urgent':
                record.color = 9  # Rouge vif - URGENT
            elif record.state == 'done':
                record.color = 10  # Vert
            elif record.state == 'with_doctor':
                record.color = 4  # Bleu
            else:
                record.color = 0  # Blanc
    
    @api.constrains('appointment_date', 'appointment_time', 'doctor_id')
    def _check_appointment_validity(self):
        """Validations"""
        for record in self:
            # Vérifier heure valide
            if record.appointment_time < 0 or record.appointment_time >= 24:
                raise ValidationError(_('L\'heure doit être entre 00:00 et 23:59'))
            
            # Vérifier doublon (même médecin, même date/heure)
            duplicate = self.search([
                ('id', '!=', record.id),
                ('doctor_id', '=', record.doctor_id.id),
                ('appointment_date', '=', record.appointment_date),
                ('appointment_time', '=', record.appointment_time),
                ('state', 'not in', ['cancelled'])
            ])
            if duplicate:
                raise ValidationError(_(
                    f'Le Dr. {record.doctor_id.name} a déjà un rendez-vous '
                    f'le {record.appointment_date} à {record.display_time}'
                ))
    
    def action_set_waiting(self):
        """Passer en attente"""
        self.write({'state': 'waiting'})
    
    def action_set_with_doctor(self):
        """Passer chez le médecin"""
        self.write({'state': 'with_doctor'})
    
    def action_set_done(self):
        """Marquer comme terminé"""
        self.write({'state': 'done'})
    
    def action_cancel(self):
        """Annuler le rendez-vous"""
        self.write({'state': 'cancelled'})
        self.message_post(body="Rendez-vous annulé", subject="Annulation")
    
    def action_create_consultation(self):
        """Créer consultation depuis RDV (médecin uniquement)"""
        self.ensure_one()
        
        if self.consultation_id:
            # Si consultation existe déjà, l'ouvrir
            return {
                'name': 'Consultation',
                'type': 'ir.actions.act_window',
                'res_model': 'clinic.consultation',
                'view_mode': 'form',
                'res_id': self.consultation_id.id,
                'target': 'current',
            }
        
        # Créer nouvelle consultation
        consultation = self.env['clinic.consultation'].create({
            'patient_id': self.patient_id.id,
            'doctor_id': self.doctor_id.id,
            'appointment_id': self.id,
            'consultation_date': fields.Datetime.now(),
        })
        
        self.write({
            'consultation_id': consultation.id,
            'state': 'with_doctor'
        })
        
        return {
            'name': 'Consultation Médicale',
            'type': 'ir.actions.act_window',
            'res_model': 'clinic.consultation',
            'view_mode': 'form',
            'res_id': consultation.id,
            'target': 'current',
        }
    
    def send_confirmation_email(self):
        """Envoyer email de confirmation automatique"""
        self.ensure_one()
        
        if not self.patient_id.email:
            return False
        
        template = self.env.ref('clinic.email_template_appointment_confirmation', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
            self.write({
                'email_sent': True,
                'email_sent_date': fields.Datetime.now()
            })
            self.message_post(
                body=f"Email de confirmation envoyé à {self.patient_id.email}",
                subject="Confirmation RDV"
            )
        return True
    
    def action_resend_email(self):
        """Renvoyer email de confirmation manuellement"""
        for record in self:
            record.send_confirmation_email()