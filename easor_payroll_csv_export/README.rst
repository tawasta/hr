.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================
Easor CSV Export
================

This module generates CSV files for exporting employee and payroll data to
Easor.

Generated CSV files are stored as ``ir.attachment`` records, and also saved
to disk under ``<data_dir>/easor/``.

Features
========

* Export employee data to CSV.
* Export payroll expense data to CSV.
* Generate CSV files automatically using scheduled actions.
* Store generated CSV files as Odoo attachments.
* Save generated CSV files to disk, for pickup by an external process
  (e.g. a file transfer to Easor).

Configuration
=============

* Adjust the cron scheduler frequency if needed.

Usage
=====

Employee export
---------------

The scheduled employee export generates a CSV file containing employee master
data in the format required by Easor Payroll.

Payroll export
--------------

The scheduled payroll export generates a CSV file based on approved expense
records.

Credits
=======

Contributors
------------

* Valtteri Lattu <valtteri.lattu@futural.fi>
* Jarmo Kortetjärvi <jarmo.kortetjarvi@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy.
