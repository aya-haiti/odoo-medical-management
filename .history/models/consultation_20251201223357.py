# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Consultation(models.Model):
    _name = 'clinic.consultation'
    _description = 'Consultation Médicale'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'consultation_date desc'
    _rec_name = 'reference'
    
    # Référence unique
    reference = fields.Char(string='Référence', required=True, copy=False,
                           readonly=True, default='Nouveau', index=True)
    
    # Patient et Médecin
    patient_id = fields.Many2one('clinic.patient', string='Patient',
                                required=True, tracking=True, index=True)
    doctor_id = fields.Many2one('clinic.doctor', string='Médecin',
                               required=True, tracking=True, index=True)
    appointment_id = fields.Many2one('clinic.appointment', string='Rendez-vous',
                                    tracking=True)
    
    # Date/Heure consultation
    consultation_date = fields.Datetime(string='Date/Heure Consultation',
                                       required=True, default=fields.Datetime.now,
                                       tracking=True, index=True)
    
    # Durée
    duration = fields.Float(string='Durée (minutes)', default=30)
    
    # SIGNES VITAUX
    temperature = fields.Float(string='Température (°C)', digits=(3, 1))
    blood_pressure_systolic = fields.Integer(string='Tension Systolique')
    blood_pressure_diastolic = fields.Integer(string='Tension Diastolique')
    blood_pressure = fields.Char(string='Tension Artérielle',
                                 compute='_compute_blood_pressure',
                                 store=True)
    pulse = fields.Integer(string='Pouls (bpm)')
    respiratory_rate = fields.Integer(string='Fréquence Respiratoire (/min)')
    weight = fields.Float(string='Poids (kg)', digits=(5, 2))
    height = fields.Float(string='Taille (cm)', digits=(5, 1))
    bmi = fields.Float(string='IMC', compute='_compute_bmi', store=True, digits=(4, 2))
    oxygen_saturation = fields.Float(string='Saturation O2 (%)', digits=(3, 1))
    
    # CONSULTATION MÉDICALE
    chief_complaint = fields.Text(string='Motif de Consultation', tracking=True)
    symptoms = fields.Text(string='Symptômes Détaillés', tracking=True)
    diagnosis = fields.Text(string='Diagnostic', tracking=True)
    observations = fields.Text(string='Observations Cliniques', tracking=True)
    treatment_plan = fields.Text(string='Plan de Traitement', tracking=True)
    
    # Examens cliniques
    physical_examination = fields.Text(string='Examen Physique')
    
    # RECOMMANDATIONS
    recommendations = fields.Text(string='Recommandations et Conseils')
    follow_up_date = fields.Date(string='Date de Suivi Recommandée')
    referral = fields.Text(string='Orientation/Référence vers Spécialiste')
    
    # Relations - CORRIGÉ
    prescription_ids = fields.One2many('clinic.prescription', 'consultation_id',
                                      string='Ordonnances', copy=False)
    attachment_ids = fields.Many2many('ir.attachment', 
                                     'clinic_consultation_attachment_rel',
                                     'consultation_id', 'attachment_id',
                                     string='Fichiers Médicaux',
                                     help='Radios, analyses, scanners, photos...')
    
    # Compteurs
    prescription_count = fields.Integer(string='Nombre d\'Ordonnances',
                                       compute='_compute_prescription_count')
    attachment_count = fields.Integer(string='Nombre de Fichiers',
                                     compute='_compute_attachment_count')
    
    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('in_progress', 'En Cours'),
        ('done', 'Terminée'),
        ('cancelled', 'Annulée')
    ], string='État', default='draft', tracking=True, required=True)
    
    # Notes privées médecin
    private_notes = fields.Text(string='Notes Privées Médecin',
                               groups='clinic.group_clinic_doctor')
    
    # Active
    active = fields.Boolean(string='Actif', default=True)
    
    # Couleur
    color = fields.Integer(string='Couleur')
    
    @api.model
    def create(self, vals):
        """Générer référence unique"""
        if vals.get('reference', 'Nouveau') == 'Nouveau':
            vals['reference'] = self.env['ir.sequence'].next_by_code('clinic.consultation') or 'CONS-NEW'
        
        consultation = super(Consultation, self).create(vals)
        
        # Notification automatique
        consultation.message_post(
            body=f"Consultation créée pour {consultation.patient_id.name}",
            subject="Nouvelle Consultation"
        )
        
        return consultation
    
    @api.depends('blood_pressure_systolic', 'blood_pressure_diastolic')
    def _compute_blood_pressure(self):
        """Format tension: 120/80"""
        for record in self:
            if record.blood_pressure_systolic and record.blood_pressure_diastolic:
                record.blood_pressure = f"{record.blood_pressure_systolic}/{record.blood_pressure_diastolic}"
            else:
                record.blood_pressure = ""
    
    @api.depends('weight', 'height')
    def _compute_bmi(self):
        """Calcul IMC"""
        for record in self:
            if record.weight and record.height and record.height > 0:
                height_m = record.height / 100
                record.bmi = record.weight / (height_m ** 2)
            else:
                record.bmi = 0.0
    
    def _compute_prescription_count(self):
        """Compteur ordonnances"""
        for record in self:
            record.prescription_count = len(record.prescription_ids)
    
    def _compute_attachment_count(self):
        """Compteur fichiers"""
        for record in self:
            record.attachment_count = len(record.attachment_ids)
    
    def action_start(self):
        """Démarrer la consultation"""
        self.write({'state': 'in_progress'})
        self.message_post(body="Consultation démarrée", subject="Début Consultation")
    
    def action_done(self):
        """Terminer la consultation"""
        self.write({'state': 'done'})
        # Marquer le RDV comme terminé
        if self.appointment_id:
            self.appointment_id.write({'state': 'done'})
        self.message_post(body="Consultation terminée", subject="Fin Consultation")
    
    def action_cancel(self):
        """Annuler la consultation"""
        self.write({'state': 'cancelled'})
    
    def action_create_prescription(self):
        """Créer une ordonnance"""
        self.ensure_one()
        
        prescription = self.env['clinic.prescription'].create({
            'consultation_id': self.id,
            'patient_id': self.patient_id.id,
            'doctor_id': self.doctor_id.id,
        })
        
        return {
            'name': 'Ordonnance Médicale',
            'type': 'ir.actions.act_window',
            'res_model': 'clinic.prescription',
            'view_mode': 'form',
            'res_id': prescription.id,
            'target': 'current',
        }
    
    def action_view_prescriptions(self):
        """Afficher les ordonnances"""
        return {
            'name': 'Ordonnances',
            'type': 'ir.actions.act_window',
            'res_model': 'clinic.prescription',
            'view_mode': 'tree,form',
            'domain': [('consultation_id', '=', self.id)],
            'context': {'default_consultation_id': self.id}
        }
    
    def action_print_consultation(self):
        """Imprimer fiche de consultation"""
        return self.env.ref('clinic.action_report_consultation').report_action(self)