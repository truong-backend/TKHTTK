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
from datetime import datetime, timedelta

class hr_contract_extended(osv.osv):
    """
    Extended HR Contract Model with advanced tracking and notifications
    """
    _name = 'hr.contract'
    _inherit = 'hr.contract'
    
    def _contract_expiration_status(self, cr, uid, ids, field_name, arg, context=None):
        """
        Calculate contract expiration status
        """
        res = {}
        for contract in self.browse(cr, uid, ids, context=context):
            if contract.date_end:
                end_date = datetime.strptime(contract.date_end, '%Y-%m-%d')
                today = datetime.now()
                days_remaining = (end_date - today).days
                
                if days_remaining <= 0:
                    res[contract.id] = 'expired'
                elif days_remaining <= 30:
                    res[contract.id] = 'expiring_soon'
                else:
                    res[contract.id] = 'active'
            else:
                res[contract.id] = 'indefinite'
        return res
    
    _columns = {
        'contract_code': fields.char('Contract Code', size=20, required=True, help='Unique contract identifier'),
        'contract_type_detailed': fields.selection([
            ('full_time', 'Full Time'),
            ('part_time', 'Part Time'),
            ('contract_based', 'Contract Based'),
            ('freelance', 'Freelance'),
            ('internship', 'Internship'),
            ('probation', 'Probation')
        ], 'Detailed Contract Type', select=True),
        'salary_structure': fields.many2one('hr.payroll.structure', 'Salary Structure'),
        'trial_period_length': fields.integer('Trial Period (Months)', help='Length of probation period'),
        'contract_expiration_status': fields.function(_contract_expiration_status, 
                                                     method=True, 
                                                     type='selection', 
                                                     selection=[
                                                         ('active', 'Active'),
                                                         ('expiring_soon', 'Expiring Soon'),
                                                         ('expired', 'Expired'),
                                                         ('indefinite', 'Indefinite')
                                                     ], 
                                                     string='Contract Status', 
                                                     store=True),
        'additional_benefits': fields.text('Additional Benefits'),
        'performance_incentives': fields.float('Performance Incentives', digits=(10,2)),
    }
    
    _sql_constraints = [
        ('contract_code_unique', 'unique(contract_code)', 'Contract Code must be unique!'),
    ]
    
    def create(self, cr, uid, vals, context=None):
        """
        Override create method to add custom validation and auto-generation
        """
        # Generate contract code if not provided
        if not vals.get('contract_code'):
            vals['contract_code'] = self.pool.get('ir.sequence').get(cr, uid, 'hr.contract')
        
        # Set default trial period if not specified
        if not vals.get('trial_period_length'):
            vals['trial_period_length'] = 3  # Default 3 months probation
        
        return super(hr_contract_extended, self).create(cr, uid, vals, context=context)
    
    def check_expiring_contracts(self, cr, uid, context=None):
        """
        Automated method to check and notify about expiring contracts
        """
        # Search for contracts expiring within next 30 days
        today = datetime.now()
        expiry_date = today + timedelta(days=30)
        
        contract_ids = self.search(cr, uid, [
            ('date_end', '<=', expiry_date.strftime('%Y-%m-%d')),
            ('state', '!=', 'closed')
        ])
        
        # Notify HR or send emails about expiring contracts
        for contract in self.browse(cr, uid, contract_ids, context=context):
            # In a real-world scenario, implement email notification or HR alert
            print "Contract %s for %s is expiring soon" % (
                contract.contract_code, 
                contract.employee_id.name
            )
        
        return True

hr_contract_extended()