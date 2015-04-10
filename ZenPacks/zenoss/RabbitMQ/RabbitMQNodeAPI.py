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

from Products.ZenRelations.RelSchema import ToManyCont, ToOne

from .RabbitMQComponent import RabbitMQComponent


class RabbitMQNodeAPI(RabbitMQComponent):
    meta_type = "RabbitMQNodeAPI"
    portal_type = "RabbitMQNode"

    _relations = RabbitMQComponent._relations + (
        ('rabbitmq_host', ToOne(ToManyCont,
            'Products.ZenModel.Device.Device',
            'rabbitmq_apinodes',
            ),),
        ('rabbitmq_vhosts', ToManyCont(ToOne,
            'ZenPacks.zenoss.RabbitMQ.RabbitMQVHost.RabbitMQVHost',
            'rabbitmq_node',
            ),),
        )

    def device(self):
        return self.rabbitmq_host()
