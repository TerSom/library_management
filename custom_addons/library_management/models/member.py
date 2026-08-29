from odoo import models, fields, api

class LibraryMember(models.Model):
    _name = 'library.member'
    _description = 'Library Member'

    _inherits = {'res.partner' : 'partner_id'}

    partner_id = fields.Many2one('res.partner', string="Partner", required=True, ondelete='cascade')
    member_number = fields.Char(string='Member Number', required=True)

    _sql_constraints = [
        ('member_number_unique', 'UNIQUE(member_number)', 'Member number must be unique.'),
    ]
    registration_date = fields.Date(string='Registration Date', default=fields.Date.context_today)

    loan_ids = fields.One2many("library.loan", "member_id", string="Loans")
