from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class LibraryPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'loan_count' in counters:
            partner_id = request.env.user.partner_id.id
            loan_model = request.env['library.loan']
            values['loan_count'] = loan_model.sudo().search_count([
                ('member_id.partner_id', '=', partner_id),
                ('state', '=', 'ongoing'),
            ]) if loan_model.has_access('read') else 0
        return values

    @http.route(['/my/loans'], type='http', auth='user', website=True)
    def portal_my_loans(self, **kw):
        partner_id = request.env.user.partner_id.id

        loans = request.env['library.loan'].sudo().search([
            ('member_id.partner_id', '=', partner_id)
        ])

        values = {
            'loans': loans,
            'page_name': 'loan',
        }

        return request.render('library_website.portal_my_loans_template', values)

