# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Prescription(models.Model):
    _name = 'clinic.prescription'
    _description = 'Ordonnance Médicale'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'prescription_date desc'
    _rec_name = 'reference'
    
    # Référence unique
    reference = fields.Char(
        string='Référence', 
        required=True, 
        copy=False,
        readonly=True, 
        default='Nouveau', 
        index=True
    )
    
    # ========== IMPORTANT: Ce champ est OBLIGATOIRE ==========
    consultation_id = fields.Many2one(
        'clinic.consultation', 
        string='Consultation',
        required=True, 
        ondelete='cascade', 
        index=True,
        tracking=True
    )
    # =========================================================
    
    # Relations
    patient_id = fields.Many2one(
        'clinic.patient', 
        string='Patient',
        required=True, 
        tracking=True, 
        index=True
    )
    
    doctor_id = fields.Many2one(
        'clinic.doctor', 
        string='Médecin',
        required=True, 
        tracking=True, 
        index=True
    )
    
    # Date prescription
    prescription_date = fields.Date(
        string='Date Ordonnance',
        required=True, 
        default=fields.Date.today,
        tracking=True, 
        index=True
    )
    
    # Lignes de prescription (médicaments)
    line_ids = fields.One2many(
        'clinic.prescription.line', 
        'prescription_id',
        string='Médicaments Prescrits',
        copy=True
    )
    
    # Instructions générales
    instructions = fields.Text(
        string='Instructions Générales',
        help='Instructions générales pour toute l\'ordonnance'
    )
    
    # Durée du traitement
    duration_days = fields.Integer(
        string='Durée du Traitement (jours)', 
        default=7
    )
    
    # Notes privées
    notes = fields.Text(
        string='Notes Privées Médecin',
        groups='clinic.group_clinic_doctor'
    )
    
    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('validated', 'Validée'),
        ('cancelled', 'Annulée')
    ], string='État', default='draft', tracking=True, required=True)
    
    # Nombre de lignes
    line_count = fields.Integer(
        string='Nombre de Médicaments',
        compute='_compute_line_count',
        store=True
    )
    
    # Active
    active = fields.Boolean(string='Actif', default=True)
    
    # Couleur
    color = fields.Integer(string='Couleur')
    
    @api.model
    def create(self, vals):
        """Générer référence unique"""
        if vals.get('reference', 'Nouveau') == 'Nouveau':
            vals['reference'] = self.env['ir.sequence'].next_by_code('clinic.prescription') or 'ORD-NEW'
        
        prescription = super(Prescription, self).create(vals)
        
        # Notification
        prescription.message_post(
            body=f"Ordonnance créée pour {prescription.patient_id.name}",
            subject="Nouvelle Ordonnance"
        )
        
        return prescription
    
    @api.depends('line_ids')
    def _compute_line_count(self):
        """Compter les lignes de médicaments"""
        for record in self:
            record.line_count = len(record.line_ids)
    
    def action_validate(self):
        """Valider l'ordonnance"""
        self.write({'state': 'validated'})
        self.message_post(body="Ordonnance validée", subject="Validation")
    
    def action_cancel(self):
        """Annuler l'ordonnance"""
        self.write({'state': 'cancelled'})
        self.message_post(body="Ordonnance annulée", subject="Annulation")
    
    def action_set_to_draft(self):
        """Remettre en brouillon"""
        self.write({'state': 'draft'})
        self.message_post(body="Ordonnance remise en brouillon", subject="Brouillon")
    
    def action_print_prescription(self):
        """Imprimer l'ordonnance"""
        self.ensure_one()
        return self.env.ref('clinic.action_report_prescription').report_action(self)


class PrescriptionLine(models.Model):
    _name = 'clinic.prescription.line'
    _description = 'Ligne d\'Ordonnance (Médicament Prescrit)'
    _order = 'sequence, id'
    
    # Séquence pour l'ordre
    sequence = fields.Integer(string='Séquence', default=10)
    
    # Relation avec ordonnance
    prescription_id = fields.Many2one(
        'clinic.prescription', 
        string='Ordonnance',
        required=True, 
        ondelete='cascade',
        index=True
    )
    
    # Médicament
    medicine_id = fields.Many2one(
        'clinic.medicine', 
        string='Médicament',
        required=True,
        index=True
    )
    
    # Nom du médicament (pour affichage rapide)
    medicine_name = fields.Char(
        related='medicine_id.name',
        string='Nom Médicament',
        readonly=True,
        store=True
    )
    
    # Posologie détaillée
    dosage = fields.Char(
        string='Dosage', 
        required=True,
        help='Ex: 1 comprimé, 2 cuillères à soupe, 5ml'
    )
    
    frequency = fields.Char(
        string='Fréquence', 
        required=True,
        help='Ex: 3 fois par jour, toutes les 8 heures, matin et soir'
    )
    
    duration = fields.Char(
        string='Durée',
        help='Ex: 7 jours, 2 semaines, 1 mois'
    )
    
    # Instructions spécifiques pour ce médicament
    instructions = fields.Text(
        string='Instructions Spécifiques',
        help='Ex: à prendre avant les repas, avec beaucoup d\'eau, ne pas conduire'
    )
    
    # Quantité à délivrer (nombre de boîtes)
    quantity = fields.Float(
        string='Quantité à Délivrer', 
        default=1.0,
        digits=(10, 2),
        help='Nombre de boîtes/flacons à délivrer en pharmacie'
    )
    
    # Notes additionnelles
    notes = fields.Text(string='Notes')
    
    # Actif
    active = fields.Boolean(string='Actif', default=True)