# -*- coding: utf-8 -*-
{
    'name': 'Gestion Cabinet Médical',
    'version': '16.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Gestion complète d\'un cabinet médical',
    'description': """
        Module de Gestion d'un Cabinet Médical
        ========================================
        
        Fonctionnalités principales:
        * Gestion des rendez-vous avec emails automatiques
        * Gestion des patients
        * Consultations médicales complètes
        * Ordonnances avec impression PDF
        * Gestion des médicaments
    """,
    'author': 'Votre Nom',
    'website': 'https://www.votresite.com',
    'depends': ['base', 'mail'],
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Data
        'data/sequences.xml',
        'data/email_templates.xml',
        
        # Views
        'views/patient_views.xml',
        'views/doctor_views.xml',
        'views/appointment_views.xml',
        'views/consultation_views.xml',
        'views/prescription_views.xml',
        'views/medicine_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}