.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
HR Expense Portal
=================
This module extends the Odoo portal to provide employees with a dedicated
self-service interface for viewing their expenses and expense reports.

It allows portal users to:

* Browse their own expense lines
* View submitted expense reports
* Search, filter, group and sort expenses
* View expense totals and statuses
* Access attachments related to expenses
* Follow communication threads on expense records

The module adds portal menu entries and views designed to improve employee
visibility into expense tracking without granting back-office access.

Only users belonging to the **Portal: Expenses** security group can access
these features, and record rules ensure users can only see their own expenses
and expense reports.

Configuration
=============

To configure the module:

* Ensure the **Expenses** application (``hr_expense``) is installed.
* Assign portal users to the **Portal: Expenses** security group.
* Make sure employees are properly linked to users
  (Employee → Work Information → Related User), since access to
  expenses is restricted to each user's own employee record.
* Verify portal access rights if custom security rules are used.

No additional functional configuration is required.

Usage
=====

After configuration:

* Portal users can log in to the Odoo portal.
* Two new sections will appear on the portal home:

  * **Expenses** – browse individual expense lines
  * **Expense Reports** – track expense report submissions and status

Within the portal users can:

* Filter expenses by status or date ranges
* Search by description, category, or report
* Sort and group expense records
* View totals and detailed expense information
* Download attachments and follow related communications

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
