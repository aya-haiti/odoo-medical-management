# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Doctor(models.Model):
    _name = 'clinic.doctor'
    _description = 'Médecin'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'name asc'
    
    # Informations personnelles
    name = fields.Char(string='Nom Complet (Dr.)', required=True, tracking=True, index=True)
    specialization = fields.Char(string='Spécialité', required=True, tracking=True)
    
    # Coordonnées
    phone = fields.Char(string='Téléphone', required=True, tracking=True)
    email = fields.Char(string='Email Professionnel', tracking=True)
    address = fields.Text(string='Adresse Cabinet')
    
    # Informations professionnelles
    license_number = fields.Char(string='Numéro de Licence Médicale', tracking=True)
    qualification = fields.Char(string='Diplômes et Qualifications', tracking=True)
    experience_years = fields.Integer(string='Années d\'Expérience')
    
    # Photo
    image = fields.Image(string='Photo', max_width=256, max_height=256)
    
    # Relation avec utilisateur Odoo
    user_id = fields.Many2one('res.users', string='Utilisateur Odoo', 
                              tracking=True,
                              help='Lier ce médecin à un utilisateur pour le login')
    
    # Relations
    appointment_ids = fields.One2many('clinic.appointment', 'doctor_id', string='Rendez-vous')
    consultation_ids = fields.One2many('clinic.consultation', 'doctor_id', string='Consultations')
    
    # Statistiques
    appointment_count = fields.Integer(string='Nombre de RDV', compute='_compute_counts')
    consultation_count = fields.Integer(string='Nombre de Consultations', compute='_compute_counts')
    
    # Disponibilité
    available_monday = fields.Boolean(string='Lundi', default=True)
    available_tuesday = fields.Boolean(string='Mardi', default=True)
    available_wednesday = fields.Boolean(string='Mercredi', default=True)
    available_thursday = fields.Boolean(string='Jeudi', default=True)
    available_friday = fields.Boolean(string='Vendredi', default=True)
    available_saturday = fields.Boolean(string='Samedi', default=False)
    available_sunday = fields.Boolean(string='Dimanche', default=False)
    
    # Horaires
    start_time = fields.Float(string='Début Journée', default=9.0)
    end_time = fields.Float(string='Fin Journée', default=17.0)
    
    # Notes
    bio = fields.Text(string='Biographie Professionnelle')
    notes = fields.Text(string='Notes Internes')
    
    # État
    active = fields.Boolean(string='Actif', default=True)
    
    # Couleur pour affichage calendrier
    color = fields.Integer(string='Couleur', default=1)
    
    def _compute_counts(self):
        """Calcul des statistiques"""
        for record in self:
            record.appointment_count = self.env['clinic.appointment'].search_count([('doctor_id', '=', record.id)])
            record.consultation_count = self.env['clinic.consultation'].search_count([('doctor_id', '=', record.id)])
    
    def action_view_appointments(self):
        """Afficher tous les rendez-vous du médecin"""
        return {
            'name': 'Mes Rendez-vous',
            'type': 'ir.actions.act_window',
            'res_model': 'clinic.appointment',
            'view_mode': 'tree,form,calendar',
            'domain': [('doctor_id', '=', self.id)],
            'context': {'default_doctor_id': self.id}
        }
    
    def action_view_consultations(self):
        """Afficher toutes les consultations du médecin"""
        return {
            'name': 'Mes Consultations',
            'type': 'ir.actions.act_window',
            'res_model': 'clinic.consultation',
            'view_mode': 'tree,form',
            'domain': [('doctor_id', '=', self.id)],
            'context': {'default_doctor_id': self.id}
        }
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """Améliorer la recherche par nom et spécialité"""
        args = args or []
        if name:
            args = ['|', ('name', operator, name), ('specialization', operator, name)] + args
        return super(Doctor, self)._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)