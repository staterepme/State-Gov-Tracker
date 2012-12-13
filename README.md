State-Gov-Tracker
=================

Project Overview
----------------
The goal of this project is to create a simple-to-use web application that makes monitoring the activity of state elected officials  much easier for the average person. 

This web application will allow users to identify state-level elected officials who represent them based on the user's address. Then users can follow links to web pages that have information on their state legislators. The web page includes basic information about the legislator in addition to other data a user may want to use to assess their behavior such as roll call votes, social media messages (Twitter, Facebook), campaign finance, etc.

Installation Notes (very incomplete)
------------
Clone the repo (`git clone https://github.com/staterepme/State-Gov-Tracker.git`)

Install requirements using `pip install -r requirements.txt` (we suggest using a virtualenv)

Copy `settings_example.py` to `settings.py`. Modify `settings.py` and point the `DATABASES name` the MySQL server (if you want access to our development server for testing or development, ask and something may be able to be arranged).

Register for an API-key for the Sunlight Foundation at `http://services.sunlightlabs.com/accounts/register/`. Save the API key in `~/.sunlight.key`. For information see `http://python-sunlight.readthedocs.org/en/latest/index.html`.

You will also need Cicero API keys through [Azavea](http://www.azavea.com/products/cicero/) and place those in the `login_credentials.py` file for search functionality. If you do not have Cicero keys, the rest of the site should still work.

`cd` top level project directory and run `python manage.py runserver`.

Data Sources
------------
For geo-coding addresses and matching them to state legislative districts we use [Cicero](http://www.azavea.com/products/cicero/) from Azavea. We also formed an initial list of Twitter and Facebook usernames for state legislators through Cicero.

The list of members, voting history, offices, and contact information is obtained through the Sunlight Foundation's [OpenStates](http://openstates.org/).

We gather press releases ourselves using webscraping scripts. Those files can be found in the `/data_scripts` subfolder.

Modules/Packages/Etc. used for the website
------------

This website would not be possible if not for a number of great packages written for Django.

`secretballot` is a package written by James Turk. This version is slightly modified to work with our code. To see the original code, check it out on [github](https://github.com/sunlightlabs/django-secretballot).

For our responsive admin set-up we use [django-admin-bootstrapped](https://github.com/riccardo-forina/django-admin-bootstrapped).

To profile and debug the site during development, we use [django-debug-doolbar](https://github.com/django-debug-toolbar/django-debug-toolbar).

To easily make our forms compatible with Twitter Bootstrap, we use [django-forms-bootstrap](https://github.com/pinax/django-forms-bootstrap).

License
------------

State-Gov-Tracker is an open-source, free application, covered under the GPLv3 License. Please fork and experiment with it!



