.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================================
HR Skills Frontend Networking JCI
=================================

This module extends the HR Skills Frontend portal with privacy-based networking
visibility.

It allows administrators to define which privacy permission controls whether a
user's profile information is shown on the skills networking page. Only users
who have accepted the configured privacy activity are displayed on the
``/all/skills`` page.

The module also extends the employee grouped skill card with selected partner
profile information, such as job title, website, senator number, languages,
LinkedIn, employer, education level and other education details.

Configuration
=============
#. Go to the privacy activity configuration.
#. Create or open the privacy activity that should control skills networking
   visibility.
#. Enable ``Show in profile`` if the permission should be asked from the user
   on the portal profile page.
#. Enable ``Show in skills networking``.
#. Save the activity.

Users must then accept this privacy permission from their portal profile before
their information is shown on the skills networking page.

Usage
=====

#. Log in as a portal user.
#. Open the portal profile page.
#. Accept the privacy permission configured for skills networking.
#. Open ``/all/skills``.
#. The user is shown on the networking skills page only if the consent has been
   accepted.

The additional profile information shown on the skill card is read from the
related ``res.partner`` record.

Contributors
------------
* Valtteri Lattu <valtteri.lattu@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy.
