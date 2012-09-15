State-Gov-Tracker
=================

Project Overview
----------------
The goal of this project is to create a simple-to-use web application that makes monitoring the activity of state elected officials  much easier for the average person. 

This web application will allow users to identify state-level elected officials who represent them based on the user's address. Then users can follow links to web pages that have information on their MCs. The web page will include basic information about the MC in addition to other data a user may want to use to assess their MC’s behavior such as roll call votes, social media messages (Twitter, Facebook), campaign finance, etc.

Installation Notes (very incomplete)
------------
Clone the repo (`git clone https://github.com/jasonblanchard/State-Gov-Tracker.git`)

create dev.db in the top level of the repo directory

Modify State-Gov-Tracker/state_gov_tracker/settings.py
- DATABASES= { 'NAME': 'PATH_TO_dev.db' }

TEMPLATE_DIRS

Load tables into database:

`python manage.py syncdb`



