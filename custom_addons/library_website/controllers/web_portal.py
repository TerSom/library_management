from odoo import http
from odoo.http import request

class LibraryPortal(http.Controller):
    
    @http.route(['/my/loans'], type='http', auth='user', website=True)
    def portal_my_loans(self,**kw):
        partner_id = request.env.user.partner_id.id

        loans = request.env['library.loan'].sudo().search([
            ('member_id.partner_id', '=' , partner_id)
        ])

        values = {
            'loans' : loans
        }
        
        return request.render('library_website.portal_my_loans_template', values)
