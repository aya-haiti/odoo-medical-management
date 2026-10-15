# -*- coding: utf-8 -*-

from odoo import models, fields


class Medicine(models.Model):
    _name = 'clinic.medicine'
    _description = 'Médicament'
    _rec_name = 'name'
    _order = 'name asc'
    
    # Informations principales
    name = fields.Char(string='Nom Commercial', required=True, index=True)
    generic_name = fields.Char(string='Nom Générique (DCI)')
    
    # Catégorie
    category = fields.Selection([
        ('antibiotic', 'Antibiotique'),
        ('painkiller', 'Antalgique/Antidouleur'),
        ('antipyretic', 'Antipyrétique'),
        ('antihistamine', 'Antihistaminique'),
        ('anti_inflammatory', 'Anti-inflammatoire'),
        ('antiviral', 'Antiviral'),
        ('antifungal', 'Antifongique'),
        ('vitamin', 'Vitamine/Complément'),
        ('cardiovascular', 'Cardiovasculaire'),
        ('digestive', 'Système Digestif'),
        ('respiratory', 'Système Respiratoire'),
        ('other', 'Autre')
    ], string='Catégorie Thérapeutique', default='other', required=True)
    
    # Forme pharmaceutique
    dosage_form = fields.Selection([
        ('tablet', 'Comprimé'),
        ('capsule', 'Gélule'),
        ('syrup', 'Sirop'),
        ('suspension', 'Suspension'),
        ('injection', 'Injectable'),
        ('cream', 'Crème/Pommade'),
        ('drops', 'Gouttes'),
        ('spray', 'Spray'),
        ('powder', 'Poudre'),
        ('suppository', 'Suppositoire'),
        ('other', 'Autre')
    ], string='Forme Pharmaceutique', default='tablet', required=True)
    
    # Dosage
    strength = fields.Char(string='Dosage/Concentration', help='Ex: 500mg, 5mg/ml')
    
    # Fabricant
    manufacturer = fields.Char(string='Laboratoire/Fabricant')
    
    # Prix (optionnel)
    price = fields.Float(string='Prix Unitaire (DH)', digits=(10, 2))
    
    # Informations médicales
    description = fields.Text(string='Description et Indications')
    side_effects = fields.Text(string='Effets Secondaires Possibles')
    contraindications = fields.Text(string='Contre-indications')
    dosage_instructions = fields.Text(string='Instructions de Dosage Standard')
    
    # Prescription
    requires_prescription = fields.Boolean(string='Sur Ordonnance Uniquement', default=True)
    
    # Image
    image = fields.Image(string='Photo du Médicament', max_width=128, max_height=128)
    
    # Notes
    notes = fields.Text(string='Notes Internes')
    
    # État
    active = fields.Boolean(string='Actif', default=True)
    
    # Pour affichage
    color = fields.Integer(string='Couleur')
    
    def name_get(self):
        """Personnaliser l'affichage du nom"""
        result = []
        for record in self:
            if record.strength:
                name = f"{record.name} ({record.strength})"
            else:
                name = record.name
            result.append((record.id, name))
        return result