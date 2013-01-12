
# Add Bill URLs to bill information #

from sunlight import openstates
import pprint
from load_database import *

bill_queryset = session.query(pa_bills).all()

for (offset, bill) in enumerate(bill_queryset):
    if not offset % 50:
        print offset
        session.commit()
    openstates_data = openstates.bill_detail(bill_id=bill.bill_id,
        state="pa", session="2011-2012")
    if openstates_data['sources'][0]['url']:
        bill.bill_url = openstates_data['sources'][0]['url']
    else:
        bill.bill_url = None
    session.add(bill)

session.commit()