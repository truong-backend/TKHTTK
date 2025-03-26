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
import time
from datetime import datetime, timedelta

class hr_attendance_extended(osv.osv):
    """
    Extended HR Attendance Model with advanced tracking and calculations
    """
    _name = 'hr.attendance'
    _inherit = 'hr.attendance'
    
    def _calculate_worked_hours(self, cr, uid, ids, field_name, arg, context=None):
        """
        Calculate worked hours for each attendance record
        """
        res = {}
        for attendance in self.browse(cr, uid, ids, context=context):
            if attendance.action == 'sign_in' or attendance.action == 'sign_out':
                # Only calculate if we have both sign in and sign out
                sign_in = datetime.strptime(attendance.name, '%Y-%m-%d %H:%M:%S')
                res[attendance.id] = 0.0
            
                # Look for corresponding sign-out record
                sign_out_ids = self.search(cr, uid, [
                    ('employee_id', '=', attendance.employee_id.id),
                    ('name', '>', attendance.name),
                    ('action', '=', 'sign_out')
                ], order='name', limit=1)
                
                if sign_out_ids:
                    sign_out = self.browse(cr, uid, sign_out_ids[0], context=context)
                    sign_out_time = datetime.strptime(sign_out.name, '%Y-%m-%d %H:%M:%S')
                    
                    # Calculate hours worked
                    worked_duration = sign_out_time - sign_in
                    res[attendance.id] = worked_duration.total_seconds() / 3600.0
        
        return res
    
    _columns = {
        'worked_hours': fields.function(_calculate_worked_hours, 
                                        method=True, 
                                        type='float', 
                                        string='Worked Hours', 
                                        help='Total hours worked in this attendance record'),
        'attendance_status': fields.selection([
            ('normal', 'Normal Attendance'),
            ('late', 'Late Arrival'),
            ('early_leave', 'Early Leave'),
            ('overtime', 'Overtime'),
            ('missing_sign', 'Missing Sign')
        ], 'Attendance Status', select=True),
        'notes': fields.text('Attendance Notes'),
    }
    
    def create(self, cr, uid, vals, context=None):
        """
        Override create method to add attendance status
        """
        # Determine attendance status based on company work hours
        # This is a simplified version and would need more complex logic in real-world scenario
        employee_obj = self.pool.get('hr.employee')
        employee = employee_obj.browse(cr, uid, vals.get('employee_id'), context=context)
        
        # Assuming standard work hours are 9 AM to 6 PM
        if vals.get('action') == 'sign_in':
            sign_in_time = datetime.strptime(vals.get('name'), '%Y-%m-%d %H:%M:%S')
            if sign_in_time.hour > 9:
                vals['attendance_status'] = 'late'
        
        if vals.get('action') == 'sign_out':
            sign_out_time = datetime.strptime(vals.get('name'), '%Y-%m-%d %H:%M:%S')
            if sign_out_time.hour < 18:
                vals['attendance_status'] = 'early_leave'
        
        return super(hr_attendance_extended, self).create(cr, uid, vals, context=context)
    
    def check_missed_sign(self, cr, uid, context=None):
        """
        Automated method to check and mark missed sign-ins/sign-outs
        """
        # Search for employees with missing sign-in or sign-out
        employee_obj = self.pool.get('hr.employee')
        employee_ids = employee_obj.search(cr, uid, [])
        
        for employee in employee_obj.browse(cr, uid, employee_ids, context=context):
            # Get today's date
            today = time.strftime('%Y-%m-%d')
            
            # Check for missing sign-in or sign-out
            attendance_ids = self.search(cr, uid, [
                ('employee_id', '=', employee.id),
                ('name', 'like', today),
            ])
            
            if not attendance_ids:
                # Create a missing sign record
                self.create(cr, uid, {
                    'employee_id': employee.id,
                    'name': today + ' 00:00:00',
                    'action': 'sign_out',
                    'attendance_status': 'missing_sign',
                    'notes': 'Missed sign-in/sign-out'
                })
        
        return True

hr_attendance_extended()