import io
import base64
import xlsxwriter
from odoo.exceptions import ValidationError

from odoo import fields, models


class LoanExcelReportWizard(models.TransientModel):
    _name = "loan.excel.report.wizard"
    _description = "Library Loan Excel Report"

    date_from = fields.Date(
        string="From Date",
        required=True,
    )

    date_to = fields.Date(
        string="To Date",
        required=True,
    )

    def action_export_excel(self):
        self.ensure_one()

        domain = [
            ("date_borrow", ">=", self.date_from),
            ("date_borrow", "<=", self.date_to),
        ]

        if self.date_from > self.date_to:
            raise ValidationError("From Date cannot be greater than To Date.")

        loans = self.env["library.loan"].search(domain)

        if not loans:
            raise ValidationError("No loans found for the selected date range.")

        # Buat file Excel di memory
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        sheet = workbook.add_worksheet("Library Loan Report")

        # Format
        header = workbook.add_format({
            "bold": True,
            "bg_color": "#1F497D",
            "font_color": "#FFFFFF",
            "border": 1,
            "align": "center",
            "valign": "vcenter",
        })

        cell = workbook.add_format({
            "border": 1,
        })

        date_format = workbook.add_format({
            "border": 1,
            "num_format": "YYYY-MM-DD",
            "align": "left",
        })

        money_format = workbook.add_format({
            "border": 1,
            "num_format": '"Rp" #,##0',
        })

        # Judul
        sheet.merge_range(
            "A1:E1",
            "Library Loan Report",
            header
        )

        # Informasi filter
        sheet.write(2, 0, "Date From:")
        sheet.write(2, 3, "Date To:")

        sheet.write_datetime(
            2,
            1,
            self.date_from,
            workbook.add_format({"num_format": "YYYY-MM-DD"})
        )

        sheet.write_datetime(
            2,
            4,
            self.date_to,
            workbook.add_format({"num_format": "YYYY-MM-DD"})
        )

        # Header table
        sheet.write(5, 0, "No. Referensi", header)
        sheet.write(5, 1, "Member", header)
        sheet.write(5, 2, "Tanggal Pinjam", header)
        sheet.write(5, 3, "Tenggat Waktu", header)
        sheet.write(5, 4, "Total Denda", header)

        # Data
        row = 6

        for loan in loans:
            sheet.write(
                row,
                0,
                loan.name or "",
                cell
            )

            sheet.write(
                row,
                1,
                loan.member_id.partner_id.name or "",
                cell
            )

            if loan.date_borrow:
                sheet.write_datetime(
                    row,
                    2,
                    loan.date_borrow,
                    date_format
                )
            else:
                sheet.write(row, 2, "", cell)

            if loan.date_return_expected:
                sheet.write_datetime(
                    row,
                    3,
                    loan.date_return_expected,
                    date_format
                )
            else:
                sheet.write(row, 3, "", cell)

            sheet.write(
                row,
                4,
                loan.total_late_fee,
                money_format
            )

            row += 1

        sheet.set_column("A:A", 18)
        sheet.set_column("B:B", 25)
        sheet.set_column("C:D", 18)
        sheet.set_column("E:E", 18)

        workbook.close()
        output.seek(0)

        attachment = self.env["ir.attachment"].create({
            "name": "Library_Loan_Report.xlsx",
            "type": "binary",
            "datas": base64.b64encode(output.read()),
            "mimetype": (
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
        })


        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }