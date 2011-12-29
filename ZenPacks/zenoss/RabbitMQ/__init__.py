###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

"""
Custom ZenPack initialization code. All code defined in this module will be
executed at startup time in all Zope clients.
"""

import logging
log = logging.getLogger('zen.RabbitMQ')

from Products.ZenEvents.EventManagerBase import EventManagerBase
from Products.ZenModel.Device import Device
from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenRelations.RelSchema import ToManyCont, ToOne

ZENPACK_NAME = 'ZenPacks.zenoss.RabbitMQ'

# Define new device relations.
NEW_DEVICE_RELATIONS = (
    ('rabbitmq_nodes', 'RabbitMQNode'),
    )

# Add new relationships to Device if they don't already exist.
for relname, modname in NEW_DEVICE_RELATIONS:
    if relname not in (x[0] for x in Device._relations):
        Device._relations += (
            (relname, ToManyCont(ToOne,
                '.'.join((ZENPACK_NAME, modname)), 'rabbitmq_host')),
            )


class ZenPack(ZenPackBase):
    """
    ZenPack loader that handles custom installation and removal tasks.
    """

    def install(self, app):
        super(ZenPack, self).install(app)
        self._buildDeviceRelations()

    def remove(self, app, leaveObjects=False):
        if not leaveObjects:
            # Remove our Device relations additions.
            Device._relations = tuple(
                [x for x in Device._relations \
                    if x[0] not in NEW_DEVICE_RELATIONS])

            self._buildDeviceRelations()

    def _buildDeviceRelations(self):
        log.info("Rebuilding relations for existing devices")
        for d in self.dmd.Devices.getSubDevicesGen():
            d.buildRelations()


# We need to filter RabbitMQ components by id instead of name.
EventManagerBase.ComponentIdWhere = (
    "\"(device = '%s' and component = '%s')\""
    " % (me.device().getDmdKey(), me.id)")
