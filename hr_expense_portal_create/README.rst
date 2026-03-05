.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================================
HR Expense Portal - Create Expenses
===================================

This module extends **HR Expense Portal** by adding the ability for portal users
(employees) to **create and submit expense reports directly from the portal**.

It adds a *Create expense report* button to the portal expense list page. The
creation happens in a modal dialog where the user can enter **multiple expense
lines**, optionally upload **receipt attachments** per line, and submit everything
in one go.

Additionally, the module hides the core employee SSN fields and provides a secure
wizard action for authorized users to decrypt and display an employee's Personal
Identification Number (SSN) as a temporary notification.

Key features
------------

Portal expense creation:

* Adds a **Create expense report** modal on the portal (``/my/expenses``).
* Supports **multiple lines** per submission (each line becomes one ``hr.expense``).
* Submits created expenses into a sheet using ``action_submit_expenses()``.
* Per-line **receipt upload** (image/PDF) stored as attachments and linked to the created expense.
* Only **expensable products** are selectable (``can_be_expensed = True``) and must match the current company or be shared.
* Supports date input in ``YYYY-MM-DD`` or ``dd.MM.yyyy`` (invalid input falls back to today).

Partner details update (optional):

* The modal includes partner/contact details (address and personal ID input).
* If provided, the employee's private contact (``work_contact_id``) is updated with the entered values.

Personal ID (SSN) display for HR:

* Hides the core HR fields ``ssnid`` and ``identification_id`` from the employee form.
* Adds a **Show Personal ID** button for members of the decrypt group.
* Opens a wizard that asks for a **decryption key** and displays the decrypted value
  in a notification only (never stored in plain text).

Configuration
=============

1. Install dependencies
-----------------------

Make sure the following modules are installed:

* ``hr_expense_portal`` (base portal browsing for expenses)
* ``social_security_number_management`` (encryption/decryption support for SSN)

2. Portal access and employee linking
-------------------------------------

* Ensure the portal user has a related employee (``user.employee_id``).
  If the current user has no related employee, portal creation will fail.
* Portal users must have access to the portal expense pages from ``hr_expense_portal``
  (typically via the **Portal: Expenses** group from that module).

3. Product configuration
------------------------

Only products with:

* ``Can be Expensed`` enabled (``can_be_expensed = True``)

are available in the portal dropdown. Products must belong to the user's company
or be shared (no company set).

4. Security groups
------------------

* Portal expense creation uses an access rule for portal users to create/read/write
  expenses through the portal flow.
* The employee Personal ID decryption wizard is restricted to the group
  ``social_security_number_management.group_decrypt_social_security_number``.

Usage
=====

Create an expense report from the portal
----------------------------------------

1. Log in as a portal user and go to:

   * ``My Account → Expenses`` (URL: ``/my/expenses``)

2. Click **Create expense report**.
3. Fill in one or more expense lines:

   * Date
   * Category (expensable product)
   * Description
   * Quantity
   * Unit price
   * Optional receipt attachment (image/PDF)
   * Optional internal notes

4. Click **Create report**.

Result:

* One ``hr.expense`` is created per line
* Receipts are attached to their respective expense lines
* Expenses are submitted (and typically grouped into an expense sheet by Odoo)

If creation succeeds you will see ``create_ok=1`` success feedback.
If validation fails or an error occurs you will see ``create_error=1``.

Show employee Personal ID (authorized HR users)
-----------------------------------------------

1. Open an employee form.
2. Click **Show Personal ID** (visible only to users in the decrypt group).
3. Enter the decryption key in the wizard and click **Decrypt**.

The decrypted value is shown in a temporary notification and is not stored in
plain text.

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
