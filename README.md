State-Gov-Tracker
=================

Project Overview
----------------
The goal of this project is to create a simple-to-use web application that makes monitoring the activity of state elected officials  much easier for the average person. 

This web application will allow users to identify state-level elected officials who represent them based on the user's address. Then users can follow links to web pages that have information on their MCs. The web page will include basic information about the MC in addition to other data a user may want to use to assess their MC’s behavior such as roll call votes, social media messages (Twitter, Facebook), campaign finance, etc.

Installation Notes (very incomplete)
------------
Clone the repo (`git clone https://github.com/jasonblanchard/State-Gov-Tracker.git`)

Copy `StateGovTracker.db` from dropbox file to project directory.

Copy `settings_example.py` to `settings.py`. Modify `settings.py` and point the `DATABASES name` to your local `StateGovTracker.db` file

Run `pip install -r requirements.txt` in project directory in order to install dependencies.

Register for an API-key for the Sunlight Foundation at `http://services.sunlightlabs.com/accounts/register/`. Save the API key in `~/.sunlight.key`. For information see `http://python-sunlight.readthedocs.org/en/latest/index.html`.

`cd` top level project directory and run `python manage.py runserver`.

License
------------

State-Gov-Tracker is an open-source, free application, covered under the GPLv3 License. Please fork and experiment with it!



