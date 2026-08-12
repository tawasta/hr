.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
HR Skills Frontend
==================
Provides a modern portal-style listing of employee skills (``hr.employee.skill``) on the website.  
Includes search, sorting, grouping, and sidebar filters for skills and levels.  
Also adds a **“My skills”** portal modal where employees can manage their own skills.

Configuration
=============
The module includes an optional **timed access** control for the Skills portal page.

Access management is controlled by the system parameter:

  ``hr_skills_portal_access.enable``

* **0** or missing → All portal users with access to the website may view skills
* **1** → Access requires a valid **timed grant**

Timed grants are configured in Odoo via:

**Settings → Users → Skills Portal → Timed Grants**

* Grants specify a **start** and **end** timestamp
* Access is automatically revoked when the grant expires
* A scheduled job periodically archives expired entries
* A **Quick Grant** wizard on the user form allows rapid creation of accesses

If timed access is not enabled, no further configuration is required.

Additionally, the parameter
``hr_skills_frontend.mode``
controls whether users can add **one skill at a time** (`single`) or **all skills of a type at once** (`type_all`) in the “My skills” modal.

The employee form's **Related User** field (``hr.employee.user_id``) can be
linked to a portal user, not only an internal one — the standard HR domain
that hides portal users from that field's dropdown is relaxed by this
module. This lets an admin manually create an ``hr.employee`` record and
link it to an existing portal contact so that contact can manage their own
skills via the **My skills** portal modal.

Usage
=====
Install this module from Apps.  
Open ``/all/skills`` in your browser or use the **Skills** link in the website menu.

**On the Skills listing page:**
- Use the **search bar** to filter, sort and group results
- Use the sidebar to filter by **Skills** and **Levels**
- Filters use **AND semantics** — employees must match all selected criteria
- Results are paginated and can be grouped by employee, department, type, skill or level

**On the portal home:**
- Click the **My skills** button to open a management modal
- Add new skills with dependent dropdowns (Skill Type → Skill, Level)
- Remove existing skill entries by checking and saving
- Only the current user's own employee record can be updated

Features
--------
* Modern website listing for employee skills
* Search, sort, and group options with a dynamic search bar
* Sidebar filtering with **AND** matching logic
* Paginated tables with employee, department, skill and progress info
* Portal modal for self-service skill management
* Optional timed access restriction for deployments where HR wants controlled visibility

Contributors
------------
* Valtteri Lattu <valtteri.lattu@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy.
