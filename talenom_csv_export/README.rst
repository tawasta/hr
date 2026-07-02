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
* Optionally configure the system parameter
  ``talenom_csv_export.use_headers`` (``True``/``False``) to control
  whether generated CSV files include a header row. Defaults to
  ``True`` if not set.

Usage
=====

Employee export
---------------

The scheduled employee export generates a CSV file containing employee master
data in the format required by Talenom Payroll.

Payroll export
--------------

The scheduled payroll export generates a CSV file based on approved expense
records.

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
