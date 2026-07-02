.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
Talenom CSV Export
==================

This module generates CSV files for importing employee and payroll data into
Talenom Payroll.

Generated CSV files are stored as ``ir.attachment`` records.

Features
========

* Export employee master data to CSV.
* Export payroll expense data to CSV.
* Generate CSV files automatically using scheduled actions.
* Store generated CSV files as Odoo attachments.

Configuration
=============

Before using this module:

* Configure the system parameter
  ``social_security_number_encryption_key``.
* Ensure employee master data is complete.
* Configure expense analytics according to your reporting requirements.
* Set the **Talenom Company Code** field on every company (``res.company``)
  that should be exported. This code is used as the numeric prefix of the
  generated CSV filenames (e.g. ``13214``). Companies without a code
  configured are skipped, with a warning logged.
* Optionally configure the system parameter
  ``talenom_csv_export.use_headers`` (``True``/``False``) to control
  whether generated CSV files include a header row. Defaults to
  ``True`` if not set.

Usage
=====

Employee export
---------------

The scheduled employee export generates one CSV file per company containing
employee master data in the format required by Talenom Payroll. Only active
employees with a job position (``job_id``) set are included.

Payroll export
--------------

The scheduled payroll export generates one CSV file per company based on
approved expense records. An expense is included only if its **Export to
Talenom** (``talenom_export``) checkbox is enabled (enabled by default) and
it has not already been exported (``talenom_export_date`` is not set). Once
exported, the expense's ``talenom_export_date`` is stamped so it is not
included again.

Both exports group records by company and use each company's **Talenom
Company Code** as the filename prefix.

Credits
=======

Contributors
------------

* Valtteri Lattu <valtteri.lattu@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy.
