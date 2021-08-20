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

from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenModel.ZenossSecurity import ZEN_CHANGE_DEVICE
from Products.ZenUtils.Version import getVersionTupleFromString


class RabbitMQComponent(DeviceComponent, ManagedEntity):
    """
    Abstract base class to avoid repeating boilerplate code in all of the
    DeviceComponent subclasses in this ZenPack.
    """

    rabbit_version = None

    # Disambiguate multi-inheritence.
    _properties = ManagedEntity._properties
    _relations = ManagedEntity._relations

    _properties = _properties + (
        {
            'id': 'rabbit_version', 'type': 'int', 'mode': 'w'
        },
    )
    # This makes the "Templates" component display available.
    factory_type_information = ({
        'actions': ({
            'id': 'perfConf',
            'name': 'Template',
            'action': 'objTemplates',
            'permissions': (ZEN_CHANGE_DEVICE,),
            },),
        },)

    # Query for events by id instead of name.
    event_key = "ComponentId"

    # Commands are run via SSH and should not be specified absolutely.
    zCommandPath = ''

    @property
    def rabbitmq_version_flag(self):
        flag = ''
        if self.rabbit_version:
            if getVersionTupleFromString(self.rabbit_version) >= \
                    getVersionTupleFromString("3.8.0"):
                flag = '-s'
        return flag
