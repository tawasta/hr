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
No special configuration is required.  
Simply install the module and make sure the **HR Skills** core module is installed and configured.

Usage
=====
Install this module from Apps.  
Navigate to **Website → Skills** or open ``/all/skills`` in your browser.

**On the skills listing page:**
- Use the **search bar** to filter, sort and group records.
- Use the **sidebar** to select one or more **Skills** and/or **Levels**.  
  Filters use **AND semantics**, meaning employees must match all selected skills/levels.
- Results are displayed with pagination, and grouped according to the chosen grouping.

**On the portal home:**
- Click the **My skills** button to open a modal.
- Add a new skill by choosing a **Skill Type**. The dependent **Skill** and **Level** fields will update automatically.
- Remove existing skills by ticking the checkboxes and saving.
- Only the current user’s own employee record is affected.

Features
--------
* Search bar with **search in**, **sort by**, and **group by** options.
* Sidebar filters for multiple skills and/or levels.
* **AND semantics** for filters: employees must match all selected skills/levels.
* Paginated results with employee, department, skill type, skill, level, and progress.
* Portal modal for end-users to add or remove their own skills, with dependent dropdowns (Skill Type → Skill, Level).


Contributors
------------

* Valtteri Lattu <valtteri.lattu@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy.
