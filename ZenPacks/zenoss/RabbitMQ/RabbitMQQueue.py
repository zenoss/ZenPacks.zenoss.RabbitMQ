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


class RabbitMQQueue(RabbitMQComponent):
    meta_type = portal_type = "RabbitMQQueue"

    durable = None
    auto_delete = None
    arguments = None

    _properties = RabbitMQComponent._properties + (
        {'id': 'durable', 'type': 'boolean', 'mode': 'w'},
        {'id': 'auto_delete', 'type': 'boolean', 'mode': 'w'},
        {'id': 'arguments', 'type': 'string', 'mode': 'w'},
        )

    _relations = RabbitMQComponent._properties + (
        ('rabbitmq_vhost', ToOne(ToManyCont,
            'ZenPacks.zenoss.RabbitMQ.RabbitMQNode.RabbitMQVHost',
            'rabbitmq_queues',
            ),),
        )
