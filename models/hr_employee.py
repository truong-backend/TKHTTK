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

from osv import osv, fields
from tools.translate import _

class hr_employee_extended(osv.osv):
    """
    Extended HR Employee Model with additional fields and functionality
    """
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    
    def _calculate_age(self, cr, uid, ids, field_name, arg, context=None):
        """
        Calculate employee age based on birthdate
        """
        result = {}
        for employee in self.browse(cr, uid, ids, context=context):
            if employee.birthday:
                from datetime import datetime
                today = datetime.now()
                birthday = datetime.strptime(employee.birthday, '%Y-%m-%d')
                age = today.year - birthday.year - \
                    ((today.month, today.day) < (birthday.month, birthday.day))
                result[employee.id] = age
            else:
                result[employee.id] = 0
        return result
    
    _columns = {
        'employee_code': fields.char('Employee Code', size=20, required=True, help='Unique employee identifier'),
        'age': fields.function(_calculate_age, method=True, type='integer', string='Age', store=True),
        'emergency_contact': fields.text('Emergency Contact Details'),
        'skills_ids': fields.many2many('hr.skills', 'employee_skills_rel', 'employee_id', 'skill_id', 'Professional Skills'),
        'education_level': fields.selection([
            ('high_school', 'High School'),
            ('bachelor', 'Bachelor Degree'),
            ('master', 'Master Degree'),
            ('phd', 'PhD'),
            ('other', 'Other')
        ], 'Education Level', select=True),
        'performance_rating': fields.float('Performance Rating', digits=(3,2), help='Annual performance rating'),
    }
    
    _sql_constraints = [
        ('employee_code_unique', 'unique(employee_code)', 'Employee Code must be unique!'),
    ]
    
    def create(self, cr, uid, vals, context=None):
        """
        Override create method to add custom validation
        """
        # Additional validation logic can be added here
        if not vals.get('employee_code'):
            vals['employee_code'] = self.pool.get('ir.sequence').get(cr, uid, 'hr.employee')
        
        return super(hr_employee_extended, self).create(cr, uid, vals, context=context)
    
    def name_get(self, cr, uid, ids, context=None):
        """
        Custom name_get to display employee code with name
        """
        if not ids:
            return []
        
        res = []
        for employee in self.browse(cr, uid, ids, context=context):
            name = '[%s] %s' % (employee.employee_code, employee.name)
            res.append((employee.id, name))
        return res

hr_employee_extended()

# Additional related model for skills
class hr_skills(osv.osv):
    """
    Professional Skills Management
    """
    _name = 'hr.skills'
    _description = 'Professional Skills'
    
    _columns = {
        'name': fields.char('Skill Name', size=100, required=True),
        'description': fields.text('Description'),
        'skill_category': fields.selection([
            ('technical', 'Technical'),
            ('soft', 'Soft Skills'),
            ('language', 'Language'),
            ('other', 'Other')
        ], 'Skill Category', required=True),
    }
    
    _sql_constraints = [
        ('skill_name_unique', 'unique(name)', 'Skill must be unique!'),
    ]

hr_skills()