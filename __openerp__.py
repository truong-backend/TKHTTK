# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Custom HR Management',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 20,
    'summary': 'Enhance HR Management Capabilities',
    'description': """
    Custom HR Module for Enhanced Employee Management
    - Advanced Employee Tracking
    - Attendance Management
    - Contract Handling
    """,
    'author': 'Your Company',
    'website': 'http://www.yourcompany.com',
    'depends': [
        'base',
        'hr',
        'hr_attendance',
        'hr_contract',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Views
        'views/hr_employee_view.xml',
        'views/hr_attendance_view.xml',
        'views/hr_contract_view.xml',
        
        # Data
        'data/hr_employee_data.xml',
        'data/hr_attendance_data.xml',
        
        # Reports
        'reports/hr_attendance_report.xml',
        'reports/hr_employee_report.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': ['static/css/hr_custom.css'],
}