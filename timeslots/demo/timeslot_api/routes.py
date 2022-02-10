# -*- coding: utf-8 -*-

###
### DO NOT CHANGE THIS FILE
### 
### The code is auto generated, your change will be overwritten by 
### code generating.
###
from __future__ import absolute_import

from .api.appointments import Appointments
from .api.appointments_cancel import AppointmentsCancel


routes = [
    dict(resource=Appointments, urls=['/appointments'], endpoint='appointments'),
    dict(resource=AppointmentsCancel, urls=['/appointments/cancel'], endpoint='appointments_cancel'),
]