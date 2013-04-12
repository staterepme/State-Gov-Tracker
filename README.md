State-Gov-Tracker
=================

Project Overview
----------------
The goal of this project is to create a simple-to-use web application that makes monitoring the activity of state elected officials  much easier for the average person. 

This web application will allow users to identify state-level elected officials who represent them based on the user's address. Then users can follow links to web pages that have information on their state legislators. The web page includes basic information about the legislator in addition to other data a user may want to use to assess their behavior such as roll call votes, social media messages (Twitter, Facebook), campaign finance, etc.

You can visit an example of this application that focuses on Pennsylvania at [StateRep.Me](www.staterep.me). We are currently working on cleaning up the project layout and making it easier to use in locales besides Pennsylvania.

Installation Notes
------------

## Overview ##
The following instructions will set up and install a StateRep.Me instance on a VM. The project will not have data in the database, but will include at least serve the homepage. (We are currently working on automating data deployment as well). If you run into issues, check the troubleshooting instructions below or open an issue on the bug tracker.

The preferred installation also requires that you have [Vagrant](http://www.vagrantup.com/) and [Ansible](http://ansible.cc/). See the documentation for those tools for installation instructions.

## The Details ##
Clone the repo (`git clone https://github.com/staterepme/State-Gov-Tracker.git`).

Copy and edit the example Ansible configuration file from the playbooks directory.
    cp playbooks/ansible_vars.example.yml playbooks/ansible_vars.yml

Open `ansible_vars.yml` in your favorite text editor and fill in the following settings.

+ `django_secret_key`: Your secret key - do not share this. See Django [documentation](https://docs.djangoproject.com/en/dev/ref/settings/#secret-key).
+ `sunlight_key`: StateRep.Me relies on some of the OpenStates APIs which require an API key. You can register [here](http://services.sunlightlabs.com/accounts/register/) (don't worry it is free).
+ `cicero_key` and `cicero_user`: You will also need Cicero API keys through [Azavea](http://www.azavea.com/products/cicero/). This service powers the matching of state legislators to longitude and latitude coordinates. You can register for a free trial [here](http://www.azavea.com/products/cicero/free-trial/).
+ `bing_key`: We use the Bing Maps API to geocode addresses. To use this service requires registration. Instructions to obtain an API key go [here](http://msdn.microsoft.com/en-us/library/ff428642.aspx).

After specifing the settings you are ready to run the `scripts/vagrant-ansible.sh` script. This will create an Ubuntu 12.04 VM for StateRep.Me that will have a local instance of StateRep.Me running and available at http://localhost:6060/.

Lastly, you will need to SSH into the VM (e.g. `vagrant ssh`) and adjust some settings for the Postgresql database. Specifically, because Postgres does not compare ints and integers by default, this can cause some errors with the current set up. If you do the following, error messages should clear up:
+ Sign into the DB as the superuser (postgres)
+ Select the staterep database (`\c staterep`)
+ Run the following command (`CREATE CAST (integer AS text) WITH INOUT AS IMPLICIT`)

Let us know if you run into any other issues!

## Common Issues ##
There are some known issues with the Ansible and Vagrant scripts depending on OS.

### File does not exist ###
When running `scripts/vagrant-ansible.sh` on some systems the location for the Vagrant SSH key is not correctly passed to the ansible-playbook script. To solve this issue you need to hard code the location of your vagrant `insecure_private_key` on line 10.

### Requirements Hang/Do Not Install ###
The Ansible script also installs the requirements for StateRep.Me. There is a known issue where the script hangs when running `pip install -r requirements.txt` for the project. If this happens, follow the following steps.
+ SSH into your vagrant vm with `vagrant ssh`
+ Activate the virtualenv for the project (should be located in your `staterep` folder.)
+ Change into the `staterep/app/` directory
+ Run `pip install -r requirements.txt` and wait for dependencies to install
+ Exit from the VM and try running the `scripts/vagrant-ansible.sh` file again.

Data Sources
------------
For geo-coding addresses and matching them to state legislative districts we use [Cicero](http://www.azavea.com/products/cicero/) from Azavea. We also formed an initial list of Twitter and Facebook usernames for state legislators through Cicero.

The list of members, voting history, offices, and contact information is obtained through the Sunlight Foundation's [OpenStates](http://openstates.org/).

We gather press releases ourselves using webscraping scripts. Those files can be found in the `/data_scripts` subfolder.

Modules/Packages/Etc. used for the website
------------

This website would not be possible if not for a number of great packages written for Django.

`secretballot` is a package written by James Turk for Sunlight Labs. This version is slightly modified to work with our code. To see the original code, check it out on [github](https://github.com/sunlightlabs/django-secretballot).

Contributors and the StateRep.Me Team
------------
StateRep.Me would not be possible without the help of many individuals and organizations who have provided advice, answered questions, and helped with some of the coding.

Jason Blanchard  
Chris Brown  
Joshua Darr  
Lauren Gilchrist  
Adam Hinz  
Charlie Milner  
Christopher Nies  
Andrew Thompson  
Nick Weingartner  

License
------------

State-Gov-Tracker is an open-source, free application, covered under the GPLv3 License. Please fork and experiment with it!

