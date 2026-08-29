from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class LibraryDashboard(models.Model):
    _name = 'library.dashboard'
    _description = 'Library Management Dashboard'

    name = fields.Char(string='Dashboard Name', default='Library Dashboard')
    
    # KPI Fields
    total_books = fields.Integer(string='Total Books', compute='_compute_kpis')
    total_members = fields.Integer(string='Total Members', compute='_compute_kpis')
    active_loans_count = fields.Integer(string='Active Loans', compute='_compute_kpis')
    overdue_loans_count = fields.Integer(string='Overdue Loans', compute='_compute_kpis')
    monthly_loans_count = fields.Integer(string='Monthly Loans', compute='_compute_kpis')
    total_late_fee = fields.Float(string='Total Late Fee', compute='_compute_kpis')

    @api.depends_context('today')
    def _compute_kpis(self):
        for record in self:
            # Total Books (active only)
            record.total_books = self.env['library.book'].search_count([('active', '=', True)])
            
            # Total Members
            record.total_members = self.env['library.member'].search_count([])
            
            # Active Loans (ongoing)
            record.active_loans_count = self.env['library.loan'].search_count([('state', '=', 'ongoing')])
            
            # Overdue Loans
            today = fields.Date.today()
            record.overdue_loans_count = self.env['library.loan'].search_count([
                ('state', '=', 'ongoing'),
                ('date_return_expected', '<', today)
            ])
            
            # Monthly Loans (this month)
            start_of_month = today.replace(day=1)
            record.monthly_loans_count = self.env['library.loan'].search_count([
                ('date_borrow', '>=', start_of_month),
                ('date_borrow', '<=', today)
            ])
            
            # Total Late Fee
            loans = self.env['library.loan'].search([])
            record.total_late_fee = sum(loans.mapped('total_late_fee'))

    def get_dashboard_data(self):
        """Return all dashboard data in one call"""
        self.ensure_one()
        
        return {
            'kpis': {
                'total_books': self.total_books,
                'total_members': self.total_members,
                'active_loans': self.active_loans_count,
                'overdue_loans': self.overdue_loans_count,
                'monthly_loans': self.monthly_loans_count,
                'total_late_fee': self.total_late_fee,
            },
            'loan_trends': self.get_loan_trend_data(),
            'popular_books': self.get_popular_books_data(),
            'overdue_loans': self.get_overdue_loans_data(),
            'recent_activities': self.get_recent_activities_data(),
            'top_members': self.get_top_members_data(),
        }

    def get_loan_trend_data(self):
        """Get loan trends for last 6 months"""
        today = fields.Date.today()
        six_months_ago = today - relativedelta(months=6)
        
        loans = self.env['library.loan'].search([
            ('date_borrow', '>=', six_months_ago),
            ('date_borrow', '<=', today)
        ])
        
        # Group by month
        monthly_data = {}
        for loan in loans:
            month_key = loan.date_borrow.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = 0
            monthly_data[month_key] += 1
        
        # Format for chart
        result = []
        current_date = six_months_ago
        for i in range(7):  # 6 months + current
            month_key = current_date.strftime('%Y-%m')
            result.append({
                'month': current_date.strftime('%b %Y'),
                'count': monthly_data.get(month_key, 0)
            })
            current_date = current_date + relativedelta(months=1)
        
        return result

    def get_popular_books_data(self):
        """Get top 10 most borrowed books"""
        query = """
            SELECT 
                b.id,
                b.name,
                COUNT(ll.id) as loan_count
            FROM library_book b
            LEFT JOIN library_loan_line ll ON ll.book_id = b.id
            WHERE b.active = true
            GROUP BY b.id, b.name
            ORDER BY loan_count DESC
            LIMIT 10
        """
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()
        
        return [{'book': r['name'], 'count': r['loan_count']} for r in results]

    def get_overdue_loans_data(self):
        """Get detailed overdue loans information"""
        today = fields.Date.today()
        overdue_loans = self.env['library.loan'].search([
            ('state', '=', 'ongoing'),
            ('date_return_expected', '<', today)
        ], order='date_return_expected asc')
        
        result = []
        for loan in overdue_loans:
            days_late = (today - loan.date_return_expected).days
            books = ', '.join(loan.loan_line_ids.mapped('book_id.name'))
            
            result.append({
                'id': loan.id,
                'name': loan.name,
                'member': loan.member_id.partner_id.name,
                'member_phone': loan.member_id.partner_id.phone or loan.member_id.partner_id.mobile,
                'books': books,
                'due_date': loan.date_return_expected.strftime('%d %b %Y'),
                'days_late': days_late,
                'late_fee': loan.total_late_fee,
            })
        
        return result

    def get_recent_activities_data(self):
        """Get latest 10 loan activities"""
        recent_loans = self.env['library.loan'].search([], order='create_date desc', limit=10)
        
        result = []
        for loan in recent_loans:
            action = 'Returned' if loan.state == 'returned' else 'Borrowed'
            books_count = len(loan.loan_line_ids)
            
            result.append({
                'id': loan.id,
                'member': loan.member_id.partner_id.name,
                'action': action,
                'date': loan.date_borrow.strftime('%d %b %Y'),
                'books_count': books_count,
                'state': loan.state,
            })
        
        return result

    def get_top_members_data(self):
        """Get top 10 most active members"""
        query = """
            SELECT 
                m.id,
                p.name,
                COUNT(l.id) as loan_count
            FROM library_member m
            LEFT JOIN res_partner p ON p.id = m.partner_id
            LEFT JOIN library_loan l ON l.member_id = m.id
            GROUP BY m.id, p.name
            ORDER BY loan_count DESC
            LIMIT 10
        """
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()
        
        return [{'member': r['name'], 'loan_count': r['loan_count']} for r in results]

    def action_view_overdue_loans(self):
        """Open overdue loans list view"""
        today = fields.Date.today()
        return {
            'name': 'Overdue Loans',
            'type': 'ir.actions.act_window',
            'res_model': 'library.loan',
            'view_mode': 'list,form',
            'domain': [('state', '=', 'ongoing'), ('date_return_expected', '<', today)],
            'context': {'create': False},
        }

    def action_view_all_loans(self):
        """Open all loans list view"""
        return {
            'name': 'All Loans',
            'type': 'ir.actions.act_window',
            'res_model': 'library.loan',
            'view_mode': 'list,form',
            'domain': [],
        }

    def action_view_books(self):
        """Open books list view"""
        return {
            'name': 'All Books',
            'type': 'ir.actions.act_window',
            'res_model': 'library.book',
            'view_mode': 'kanban,list,form',
            'domain': [('active', '=', True)],
        }

    def action_view_members(self):
        """Open members list view"""
        return {
            'name': 'All Members',
            'type': 'ir.actions.act_window',
            'res_model': 'library.member',
            'view_mode': 'list,form',
            'domain': [],
        }
