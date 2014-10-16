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

class RabbitMQAPIQueue(RabbitMQComponent):
    meta_type =  'RabbitMQAPIQueue'
    portal_type = "RabbitMQQueue"

    # Modeled attributes.
    durable = None
    auto_delete = None
    arguments = None
    api = False
    state = 'running'
    # Managed attributes.
    threshold_messages_max = None

    _properties = RabbitMQComponent._properties + (
        {'id': 'durable', 'type': 'boolean', 'mode': 'w'},
        {'id': 'auto_delete', 'type': 'boolean', 'mode': 'w'},
        {'id': 'arguments', 'type': 'string', 'mode': 'w'},
        {'id': 'threshold_messages_max', 'type': 'int', 'mode': 'w'},
        {'id': 'state', 'type': 'string', 'mode': 'w'},
        {'id': 'api', 'type': 'boolean', 'mode': 'w'},
        )

    _relations = RabbitMQComponent._relations + (
        ('rabbitmq_vhost', ToOne(ToManyCont,
            'ZenPacks.zenoss.RabbitMQ.RabbitMQVHost.RabbitMQVHost',
            'rabbitmq_queues',
            ),),
        )

    def device(self):
        return self.rabbitmq_vhost().device()

    @property
    def rabbitmq_node_name(self):
        return self.rabbitmq_vhost().rabbitmq_node().title

    @property
    def rabbitmq_vhost_name(self):
        return self.rabbitmq_vhost().title

