import base64
import csv
import io
import logging
from pathlib import Path

from odoo import api, fields, models, tools

_logger = logging.getLogger(__name__)


class TalenomCsvExport(models.Model):
    _name = "talenom.csv.export"
    _description = "Talenom CSV Export"

    CSV_DELIMITER = ";"
    CSV_ENCODING = "utf-8-sig"

    EMPLOYEE_HEADERS = [
        "henkilönumero",
        "henkilötunnus",
        "sukunimi",
        "etunimet",
        "katuosoite",
        "postinumero",
        "postitoimipaikka",
        "IBAN",
        "BIC",
        "ammattinimike",
        "työsuhteen alkupäivämäärä",
        # "kustannuspaikka",
        # "kustannuslaji",
        "voimaantulopäivämäärä",
        "vakuutuskoodi",
    ]

    PAYROLL_HEADERS = [
        "henkilönumero",
        "henkilötunnus",
        "palkkalaji",
        "määrä",
        "hinta",
        "kustannuspaikka",
        # "kustannuslaji",
        "projekti",
    ]

    def _get_employee_records(self):
        """Return employees included in the export."""
        return self.env["hr.employee"].search(
            [
                ("active", "=", True),
            ]
        )

    def _get_payroll_records(self):
        """Return expenses included in the payroll export."""
        return self.env["hr.expense"].search(
            [
                ("state", "=", "done"),
            ]
        )

    def _get_social_security_number(self, employee):
        """Return the decrypted personal identification number."""
        partner = employee.user_partner_id

        if not partner.encrypted_social_security_number:
            return ""

        key = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("social_security_number_encryption_key", default="")
            .strip()
        )

        if not key:
            _logger.error(
                "Cannot decrypt personal identification number for partner_id=%s: "
                "system parameter social_security_number_encryption_key is missing.",
                partner.id,
            )
            return ""

        decrypted = partner.decrypt_social_security_number(
            partner.encrypted_social_security_number,
            key,
        )

        if decrypted in (
            "The key you provided is incorrect.",
            "Decryption failed",
        ):
            _logger.error(
                "Cannot decrypt personal identification number for partner_id=%s.",
                partner.id,
            )
            return ""

        return decrypted

    def _get_expense_analytics(self, expense):
        cost_center = ""
        project = ""
        for account_id in expense.analytic_distribution or {}:
            analytic_account = self.env["account.analytic.account"].browse(
                int(account_id)
            )
            plan_name = analytic_account.plan_id.name
            if plan_name == "Projects":
                project = plan_name
            if plan_name == "Cost center":
                cost_center = plan_name

        return cost_center, project

    def _employee_rows(self, records=None):
        """Convert employee records into CSV rows."""
        rows = []

        for emp in records:
            rows.append(
                [
                    emp.barcode,
                    self._get_social_security_number(emp),
                    emp.user_partner_id.lastname,
                    " ".join(
                        filter(
                            None,
                            [
                                emp.user_partner_id.firstname,
                                emp.user_partner_id.firstname2,
                            ],
                        )
                    ),
                    emp.user_partner_id.street or "",
                    emp.user_partner_id.zip or "",
                    emp.user_partner_id.city or "",
                    emp.bank_account_id.acc_number,
                    emp.bank_account_id.bank_id.name,
                    emp.job_id.name or "",
                    self._format_date(emp.job_begin_date),
                    self._format_date(emp.job_begin_date),
                    "1",
                ]
            )

        return rows

    def _payroll_rows(self, records=None):
        """Convert payroll records into CSV rows."""
        rows = []

        for expense in records:
            cost_center, project = self._get_expense_analytics(expense)
            rows.append(
                [
                    expense.employee_id.barcode,
                    self._get_social_security_number(expense.employee_id),
                    expense.employee_id.job_id.contract_type_id.code,
                    expense.quantity,
                    expense.price_unit,
                    cost_center,
                    project,
                ]
            )
        return rows

    def _build_csv(self, headers, rows):
        """Build the CSV content and return it as encoded bytes."""
        buffer = io.StringIO()

        writer = csv.writer(
            buffer,
            delimiter=self.CSV_DELIMITER,
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n",
        )

        writer.writerow(headers)
        writer.writerows(rows)

        return buffer.getvalue().encode(self.CSV_ENCODING)

    def _build_filename(self, export_type):
        """Build the filename according to the Talenom naming convention."""
        today = fields.Date.context_today(self)

        if export_type == "employees":
            prefix = "13214PALKK_HLO_ODO"
        elif export_type == "payroll":
            prefix = "13214PALKK_PAL_ODO"
        else:
            raise ValueError("Unsupported Talenom CSV export type: %s" % export_type)

        return f"{prefix}_{today.strftime('%d%m%Y')}.csv"

    def _get_talenom_export_dir(self):
        """Return the directory CSV exports are saved to, creating it if needed."""
        export_dir = Path(tools.config["data_dir"]) / "talenom"
        export_dir.mkdir(parents=True, exist_ok=True)
        return export_dir

    def _save_csv_to_disk(self, filename, csv_bytes):
        """Save the generated CSV file to disk, alongside the ir.attachment."""
        file_path = self._get_talenom_export_dir() / filename
        with open(file_path, "wb") as file:
            file.write(csv_bytes)
        _logger.info("Talenom CSV saved to disk: %s", file_path)

    def _format_date(self, value):
        """Format an Odoo date value."""
        if not value:
            return ""

        if isinstance(value, str):
            value = fields.Date.from_string(value)

        return value.strftime("%d.%m.%Y")

    @api.model
    def _cron_generate_csv(self, export_type="employees"):
        """Generate the CSV and store it as an attachment."""
        if export_type == "employees":
            records = self._get_employee_records()
            headers = self.EMPLOYEE_HEADERS
            rows = self._employee_rows(records)
            description = "Talenom employee CSV export"
        elif export_type == "payroll":
            records = self._get_payroll_records()
            headers = self.PAYROLL_HEADERS
            rows = self._payroll_rows(records)
            description = "Talenom payroll CSV export"
        else:
            raise ValueError("Unsupported Talenom CSV export type: %s" % export_type)

        csv_bytes = self._build_csv(headers, rows)
        filename = self._build_filename(export_type)

        self._save_csv_to_disk(filename, csv_bytes)

        attachment = (
            self.env["ir.attachment"]
            .sudo()
            .create(
                {
                    "name": filename,
                    "type": "binary",
                    "datas": base64.b64encode(csv_bytes),
                    "mimetype": "text/csv",
                    "res_model": self._name,
                    "description": description,
                }
            )
        )

        _logger.info(
            "Talenom CSV created: export_type=%s attachment_id=%s filename=%s rows=%s",
            export_type,
            attachment.id,
            filename,
            len(rows),
        )

        return attachment
