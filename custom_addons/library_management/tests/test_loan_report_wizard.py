import base64
import io
import zipfile

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestLoanReportWizard(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.book = cls.env["library.book"].create({
            "name": "Clean Code",
            "isbn": "9780132350884",
        })
        cls.member = cls.env["library.member"].create({
            "name": "Budi",
            "member_number": "M-001",
            "member_type": "student",
        })
        cls.ongoing_loan = cls.env["library.loan"].create({
            "member_id": cls.member.id,
            "date_borrow": "2096-01-10",
            "date_return_expected": "2096-01-17",
            "state": "ongoing",
            "loan_line_ids": [(0, 0, {"book_id": cls.book.id})],
        })
        cls.draft_loan = cls.env["library.loan"].create({
            "member_id": cls.member.id,
            "date_borrow": "2096-01-11",
            "date_return_expected": "2096-01-18",
            "state": "draft",
            "loan_line_ids": [(0, 0, {"book_id": cls.book.id})],
        })

    def test_export_excludes_drafts_and_writes_date_cells(self):
        wizard = self.env["loan.excel.report.wizard"].create({
            "date_from": "2096-01-01",
            "date_to": "2096-01-31",
        })

        action = wizard.action_export_excel()
        attachment_id = int(action["url"].split("/")[3].split("?")[0])
        attachment = self.env["ir.attachment"].browse(attachment_id)
        output = io.BytesIO(base64.b64decode(attachment.datas))

        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertEqual(attachment.res_model, wizard._name)
        self.assertEqual(attachment.res_id, wizard.id)
        self.assertTrue(zipfile.is_zipfile(output))
        with zipfile.ZipFile(output) as workbook:
            sheet1_xml = workbook.read("xl/worksheets/sheet1.xml").decode()
            sheet2_xml = workbook.read("xl/worksheets/sheet2.xml").decode()
            shared_strings = workbook.read("xl/sharedStrings.xml").decode()
        self.assertIn(self.ongoing_loan.name, shared_strings)
        self.assertNotIn(self.draft_loan.name, shared_strings)
        self.assertIn("<c r=\"F7\"", sheet1_xml)
        self.assertIn("<c r=\"G7\"", sheet1_xml)
        self.assertIn("<f>COUNTA(B7:B7)</f>", sheet1_xml)
        self.assertIn("<f>SUM(K7:K7)</f>", sheet1_xml)
        self.assertIn(self.book.name, shared_strings)
        self.assertIn(self.member.name, shared_strings)

    def test_export_state_filter(self):
        wizard = self.env["loan.excel.report.wizard"].create({
            "date_from": "2096-01-01",
            "date_to": "2096-01-31",
            "state": "returned",
        })

        with self.assertRaisesRegex(ValidationError, "No confirmed loans"):
            wizard.action_export_excel()
