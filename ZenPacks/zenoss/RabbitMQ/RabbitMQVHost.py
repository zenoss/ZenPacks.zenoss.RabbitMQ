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


class RabbitMQVHost(RabbitMQComponent):
    meta_type = portal_type = "RabbitMQVHost"

    _relations = RabbitMQComponent._relations + (
        ('rabbitmq_node', ToOne(ToManyCont,
            'ZenPacks.zenoss.RabbitMQ.RabbitMQNode.RabbitMQNode',
            'rabbitmq_vhosts',
            ),),
        ('rabbitmq_apinode', ToOne(ToManyCont,
            'ZenPacks.zenoss.RabbitMQ.RabbitMQNodeAPI.RabbitMQNodeAPI',
            'rabbitmq_vhosts',
            ),),
        ('rabbitmq_exchanges', ToManyCont(ToOne,
            'ZenPacks.zenoss.RabbitMQ.RabbitMQExchange.RabbitMQExchange',
            'rabbitmq_vhost',
            ),),
        ('rabbitmq_queues', ToManyCont(ToOne,
            'ZenPacks.zenoss.RabbitMQ.RabbitMQQueue.RabbitMQQueue',
            'rabbitmq_vhost',
            ),),
        ('rabbitmq_apiqueues', ToManyCont(ToOne,
            'ZenPacks.zenoss.RabbitMQ.RabbitMQAPIQueue.RabbitMQAPIQueue',
            'rabbitmq_vhost',
            ),),
        )

    def device(self):
        return self.rabbitmq_node().device()
