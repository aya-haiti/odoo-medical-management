# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date


class Patient(models.Model):
    _name = 'clinic.patient'
    _description = 'Patient du Cabinet'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'name asc'
    
    # Informations personnelles
    name = fields.Char(string='Nom Complet', required=True, tracking=True, index=True)
    date_of_birth = fields.Date(string='Date de Naissance', tracking=True)
    age = fields.Integer(string='Âge', compute='_compute_age', store=True, readonly=True)
    
    gender = fields.Selection([
        ('male', 'Homme'),
        ('female', 'Femme'),
        ('other', 'Autre')
    ], string='Genre', tracking=True)
    
    # Coordonnées
    phone = fields.Char(string='Téléphone', required=True, tracking=True)
    email = fields.Char(string='Email', tracking=True)
    address = fields.Text(string='Adresse Complète', tracking=True)
    city = fields.Char(string='Ville', tracking=True)
    postal_code = fields.Char(string='Code Postal')
    
    # Informations médicales (visible seulement par médecin)
    blood_group = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ], string='Groupe Sanguin', tracking=True)
    
    allergies = fields.Text(string='Allergies Connues', tracking=True)
    medical_history = fields.Text(string='Antécédents Médicaux', tracking=True)
    chronic_diseases = fields.Text(string='Maladies Chroniques')
    
    # Photo du patient
    image = fields.Image(string='Photo', max_width=256, max_height=256)
    
    # Relations
    appointment_ids = fields.One2many('clinic.appointment', 'patient_id', string='Rendez-vous')
    consultation_ids = fields.One2many('clinic.consultation', 'patient_id', string='Consultations')
    
    # Statistiques
    appointment_count = fields.Integer(string='Nombre de RDV', compute='_compute_counts')
    consultation_count = fields.Integer(string='Nombre de Consultations', compute='_compute_counts')
    last_consultation_date = fields.Datetime(string='Dernière Consultation', compute='_compute_last_consultation')
    
    # Notes
    notes = fields.Text(string='Notes Internes')
    
    # État
    active = fields.Boolean(string='Actif', default=True)
    
    # Badge de couleur pour affichage
    color = fields.Integer(string='Couleur')
    
    @api.depends('date_of_birth')
    def _compute_age(self):
        """Calcul automatique de l'âge"""
        for record in self:
            if record.date_of_birth:
                today = date.today()
                born = record.date_of_birth
                record.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            else:
                record.age = 0
    
    def _compute_counts(self):
        """Calcul des statistiques"""
        for record in self:
            record.appointment_count = self.env['clinic.appointment'].search_count([('patient_id', '=', record.id)])
            record.consultation_count = self.env['clinic.consultation'].search_count([('patient_id', '=', record.id)])
    
    def _compute_last_consultation(self):
        """Date de la dernière consultation"""
        for record in self:
            last_consultation = self.env['clinic.consultation'].search([
                ('patient_id', '=', record.id),
                ('state', '=', 'done')
            ], order='consultation_date desc', limit=1)
            record.last_consultation_date = last_consultation.consultation_date if last_consultation else False
    
    def action_view_appointments(self):
        """Afficher tous les rendez-vous du patient"""
        return {
            'name': 'Rendez-vous',
            'type': 'ir.actions.act_window',
            'res_model': 'clinic.appointment',
            'view_mode': 'tree,form,calendar',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id}
        }
    
    def action_view_consultations(self):
        """Afficher toutes les consultations du patient"""
        return {
            'name': 'Consultations Médicales',
            'type': 'ir.actions.act_window',
            'res_model': 'clinic.consultation',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id}
        }
    
    @api.model
    def create(self, vals):
        """Override create pour notification automatique"""
        patient = super(Patient, self).create(vals)
        # Log dans le chatter
        patient.message_post(
            body=f"Nouveau patient créé: {patient.name}",
            subject="Création Patient"
        )
        return patient