#!/usr/bin/python

# Filename: find_leg_homepages.py
# Author:   Christopher M. Brown
# Project:  State Gov Track
# Task:     Uses openstates API to find legislator homepages

import sunlight
import pprint

import os
import sys

# Need to add django application to path #
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
split_path = os.path.split(parentdir)
sys.path.insert(0, split_path[0])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from state_gov_tracker_app.models import *
from state_gov_tracker_app.login_credentials import *

pp = pprint.PrettyPrinter(indent=4)


def get_downloaded_bills():
    """Returns list of bill_ids that have already been downloaded"""
    bill_ids = []
    for bill in session.query(pa_bills).all():
        bill_ids.append(bill.bill_id)
    return bill_ids


def get_downloaded_votes():
    """Returns list of vote_ids that have already been downloaded"""
    vote_ids = []
    for vote in session.query(votes).all():
        vote_ids.append(vote.vote_id)
    return vote_ids


def get_downloaded_legis_votes():
    """Returns list of legis_vote_ids that have already been downloaded"""
    legis_vote_ids = []
    for legis_vote in session.query(legis_votes).all():
        legis_vote_ids.append(legis_vote.vote_id)
    return legis_vote_ids


def get_legis_votes():
    """Takes vote id and downloads legislator votes and puts them in DB"""
    votes = LegisVotes.objects.filter(session="2013-2014")
    counter = 0
    for v in votes:
        if PaLegisVotes.objects.filter(vote_id=v.vote_id).exists():
            continue
        bill_votes = sunlight.openstates.bill_detail(bill_id=v.bill_id, state="pa", session="2013-2014")['votes']
        for vote in bill_votes:
            counter += 1
            print counter
            print vote['id']
            if PaLegisVotes.objects.filter(vote_id=vote['id']).exists():
                print "Vote Already Entered"
                continue
            if counter % 50 == 0:
                print "Finished getting %s Votes" % (counter)
            bill = PaBills.objects.filter(bill_id=v.bill_id, session=vote['session']).get()
            for yes_vote in vote['yes_votes']:
                new_legis_vote_yes = PaLegisVotes(legid=yes_vote['leg_id'],
                    bill_id=bill, vote=1, date=vote['date'],
                    vote_id=v)
                new_legis_vote_yes.save()
            for no_vote in vote['no_votes']:
                new_legis_vote_no = PaLegisVotes(legid=no_vote['leg_id'],
                    bill_id=bill, vote=0, date=vote['date'],
                    vote_id=v)
                new_legis_vote_no.save()
            for other_vote in vote['other_votes']:
                new_legis_vote_other = PaLegisVotes(legid=other_vote['leg_id'],
                    bill_id=bill, vote=99, date=vote['date'],
                    vote_id=v)
                new_legis_vote_other.save()


def add_bills_to_db():
    # Get Recent Bills from OpenStates #
    bills = sunlight.openstates.bills(state="PA", search_window="term")
    print "%s bills from current session" % (len(bills))
    counter = 0
    for bill in bills:
        if PaBills.objects.filter(bill_id=bill['bill_id'], session=bill['session']).exists():
            continue
        counter += 1
        print counter
        new_bill = PaBills(state="pa", session=bill['session'],
            title=bill['title'], type=bill['type'][0], chamber=bill['chamber'],
            created_at=bill['created_at'], updated_at=bill['updated_at'],
            bill_id=bill['bill_id'])
        new_bill.save()
    print "Added a total of %s bills to database" % (counter)


def add_vote_info_to_db():
    """Adds new votes to the database"""
    counter = 0
    for bill in PaBills.objects.filter(session="2013-2014")[240:]:
        counter += 1
        print counter
        bill_detail = sunlight.openstates.bill_detail(bill_id=bill.bill_id,
            state="pa", session="2013-2014")
        for vote in bill_detail['votes']:
            if LegisVotes.objects.filter(vote_id=vote['vote_id']).exists():
                continue
            print "New Vote!"
            new_vote = LegisVotes(bill_id=bill_detail['bill_id'], vote_id=vote['vote_id'],
                chamber=vote['chamber'], date=vote['date'], motion=vote['motion'],
                num_no=vote['no_count'], num_yes=vote['yes_count'],
                num_other=vote['other_count'], status=vote['passed'],
                type=vote['type'], session=vote['session'])
            new_vote.save()

if __name__ == '__main__':
    # Add New Bills to DB #
    add_bills_to_db()

    # Download Vote Information for All Bills #
    add_vote_info_to_db()

    # Download Legislator Vote Information #
    # (How each individual actually voted) #
    get_legis_votes()
