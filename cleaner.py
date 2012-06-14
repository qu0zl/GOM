#!/usr/bin/env python
import sys
import pinax
import pinax.env
from datetime import *

pinax.env.setup_environ(__file__)

# Get all the Unit objects that are:
# temporary objects, ie tempInstance = True
# older than 1 day
import gom.models
u = gom.models.Unit.objects.filter(tempInstance=True, creationTime__lt=datetime.today()-timedelta(days=1))
#delete them
u.delete()
