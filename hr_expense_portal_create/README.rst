.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================================
HR Expense Portal - Create Expenses
===================================

This module extends **HR Expense Portal** by allowing portal users to create
and submit expense reimbursement requests directly from the portal.

The module adds a **Create an Expense Reimbursement Request** button to the
portal expense list page. The request is created in a modal dialog where the
employee can fill in personal details, privacy consents, bank account details,
and one or more expense reimbursement lines.

Each submitted portal line creates one ``hr.expense`` record and the created
expenses are submitted into an expense sheet using Odoo's standard
``action_submit_expenses()`` flow.

Features
========

Portal expense reimbursement creation
-------------------------------------

* Adds a portal modal to ``/my/expenses``.
* Supports multiple expense lines in one submission.
* Creates one ``hr.expense`` per submitted line.
* Automatically submits created expenses into an expense sheet.
* Supports per-line receipt and attachment uploads.
* Supports multiple attachments per line.
* Links uploaded attachments to the created expense.
* Shows success and error feedback on the portal page.
* Supports date input in ``YYYY-MM-DD`` and ``dd.MM.YYYY`` formats.
* Falls back to today's date if the submitted date cannot be parsed.

Expense line values
-------------------

Portal users can enter:

* Date
* Expense category
* Description
* Quantity
* Unit price
* Receipt attachments
* Additional expense information

The portal stores manual price information on expenses using
``portal_manual_price``.

For portal-created expenses:

* ``quantity`` is preserved from the portal input.
* ``price_unit`` is preserved from the portal input.
* ``total_amount_currency`` is calculated as ``quantity * price_unit``.
* Odoo's default quantity reset for zero-cost expense products is bypassed.
* Odoo's default product-cost based unit price recomputation is bypassed.

This allows values such as:

* Quantity: ``2``
* Unit price: ``50``
* Total: ``100``

to remain consistent on the expense and expense sheet lines.

Expense sheet line editing
--------------------------

The module makes the following fields editable on the expense sheet line tree:

* ``quantity``
* ``price_unit``
* ``total_amount_currency``

When ``quantity`` or ``price_unit`` is changed on a portal-created expense,
``total_amount_currency`` is recalculated automatically.

Product ordering
----------------

The module adds a ``sequence`` field to ``product.product``.

Expense products in the portal dropdown are ordered by:

#. ``sequence``
#. ``name``

This allows administrators to control the order of expensable products shown in
the portal.

Product selection
-----------------

Only products that match all of the following conditions are available in the
portal:

* ``can_be_expensed = True``
* Product has no company, or product company matches the current company

Partner and employee details
----------------------------

The portal modal includes employee and partner details.

The user can submit or update:

* Personal Identification Number
* Street
* Street 2
* ZIP
* City
* Country
* Bank Account / IBAN

If an IBAN is submitted:

* The employee's existing bank account is updated, or
* A new bank account is created and linked to the employee.

Privacy consents
----------------

The module integrates with ``privacy_profile``.

Privacy activities with ``show_in_profile = True`` are shown in the portal
modal and must be accepted before the expense request can be created.

Submitted consents are stored or updated as ``privacy.consent`` records for the
employee's work contact.

Personal ID handling
--------------------

The module hides Odoo's core employee SSN fields from the employee form:

* ``ssnid``
* ``identification_id``

It adds a **Show Personal ID** button to the employee form for users in the
decryption group.

The button opens a wizard where the user must enter a decryption key. If the
key is valid, the decrypted Personal Identification Number is shown in a
temporary notification.

The decrypted value is not stored in plain text.

Configuration
=============

Dependencies
------------

The module depends on:

* ``portal``
* ``hr_expense``
* ``hr_expense_portal``
* ``social_security_number_management``
* ``privacy_profile``

Portal access
-------------

Portal users must have:

* Access to the portal expense page from ``hr_expense_portal``.
* A linked employee record via ``user.employee_id``.

If the current portal user has no linked employee, expense creation is blocked.

Expense products
----------------

Configure expense products under Products.

To make a product selectable in the portal:

* Enable ``Can be Expensed``.
* Set the company correctly, or leave company empty for a shared product.
* Set ``Sequence`` to control portal ordering.

Security
========

Personal ID decryption
----------------------

The **Show Personal ID** button is restricted to:

``social_security_number_management.group_decrypt_social_security_number``

The decryption wizard asks for a key and only displays the decrypted value in a
temporary notification.

Portal creation
---------------

Expense creation is performed through the portal controller and validates:

* Required line indexes
* Required line name
* Required product
* Product must be allowed for the current company
* Quantity must be greater than zero
* Unit price must be greater than zero
* Required privacy consents must be accepted
* Personal Identification Number is required if the partner does not already
  have an encrypted value

Usage
=====

Create an expense reimbursement request
---------------------------------------

1. Log in as a portal user.
2. Go to ``My Account → Expenses`` or ``/my/expenses``.
3. Click **Create an Expense Reimbursement Request**.
4. Fill in personal, bank, address and privacy consent details.
5. Add one or more expense reimbursement lines.
6. For each line, enter:

   * Date
   * Category
   * Description
   * Quantity
   * Unit price
   * Receipts or other attachments
   * Additional information

7. Click **Submit Expense Reimbursement for Approval**.

Result:

* One ``hr.expense`` is created per line.
* Attachments are linked to the correct expense.
* Manual portal prices are preserved.
* Expenses are submitted into an expense sheet.
* The portal redirects back to ``/my/expenses`` with success or error feedback.

Edit quantities and unit prices
-------------------------------

Authorized internal users can edit portal-created expense lines from the
expense sheet form.

When editing:

* Changing ``quantity`` recalculates the total.
* Changing ``price_unit`` recalculates the total.
* ``quantity`` and ``price_unit`` are not overwritten by the expense product's
  standard cost for portal-created expenses.

Show employee Personal ID
-------------------------

1. Open an employee form.
2. Click **Show Personal ID**.
3. Enter the decryption key.
4. Click **Decrypt**.

The decrypted value is shown in a temporary notification.

Technical notes
===============

Manual portal pricing
---------------------

The module adds:

``portal_manual_price``

to ``hr.expense``.

This flag is set to ``True`` for portal-created expenses.

When enabled:

* ``_compute_from_product`` does not reset quantity to ``1``.
* ``_needs_product_price_computation`` returns ``False``.
* ``quantity`` and ``price_unit`` are treated as manually entered values.
* ``total_amount_currency`` is recalculated from ``quantity * price_unit``.

Known behavior
==============

Odoo's standard expense model normally treats zero-cost expense products as
amount-based expenses and may reset ``quantity`` to ``1``.

This module intentionally bypasses that behavior only for portal-created
expenses marked with ``portal_manual_price``.

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