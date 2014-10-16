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

from zope.interface import implements

from Products.Zuul.decorators import info
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.component import ComponentInfo

from .interfaces import (
    IRabbitMQNodeInfo, IRabbitMQVHostInfo, IRabbitMQExchangeInfo,
    IRabbitMQQueueInfo,IRabbitMQQueueAPIInfo
    )


class RabbitMQNodeInfo(ComponentInfo):
    implements(IRabbitMQNodeInfo)

    @property
    def vhostCount(self):
        return self._object.rabbitmq_vhosts.countObjects()

    @property
    def exchangeCount(self):
        count = 0
        for vhost in self._object.rabbitmq_vhosts():
            count += vhost.rabbitmq_exchanges.countObjects()

        return count

    @property
    def queueCount(self):
        count = 0
        for vhost in self._object.rabbitmq_vhosts():
            count += vhost.rabbitmq_queues.countObjects()

        return count


class RabbitMQVHostInfo(ComponentInfo):
    implements(IRabbitMQVHostInfo)

    @property
    @info
    def rabbitmq_node(self):
        return self._object.rabbitmq_node()

    @property
    def exchangeCount(self):
        return self._object.rabbitmq_exchanges.countObjects()

    @property
    def queueCount(self):
        return self._object.rabbitmq_queues.countObjects()


class RabbitMQExchangeInfo(ComponentInfo):
    implements(IRabbitMQExchangeInfo)

    exchange_type = ProxyProperty('exchange_type')
    durable = ProxyProperty('durable')
    auto_delete = ProxyProperty('auto_delete')
    arguments = ProxyProperty('arguments')

    @property
    @info
    def rabbitmq_node(self):
        return self._object.rabbitmq_vhost().rabbitmq_node()

    @property
    @info
    def rabbitmq_vhost(self):
        return self._object.rabbitmq_vhost()


class RabbitMQQueueInfo(ComponentInfo):
    implements(IRabbitMQQueueInfo)

    durable = ProxyProperty('durable')
    auto_delete = ProxyProperty('auto_delete')
    arguments = ProxyProperty('arguments')
    state = ProxyProperty('state')
    api = ProxyProperty('api')
    @property
    def threshold_messages_max(self):
        return self._object.threshold_messages_max

    @threshold_messages_max.setter
    def threshold_messages_max(self, value):
        if value is None or value is '':
            self._object.threshold_messages_max = None
        else:
            self._object.threshold_messages_max = int(value)

    @property
    @info
    def rabbitmq_node(self):
        return self._object.rabbitmq_vhost().rabbitmq_node()

    @property
    @info
    def rabbitmq_vhost(self):
        return self._object.rabbitmq_vhost()

class RabbitMQQueueAPIInfo(ComponentInfo):
    implements(IRabbitMQQueueAPIInfo)
    
    durable = ProxyProperty('durable')
    auto_delete = ProxyProperty('auto_delete')
    arguments = ProxyProperty('arguments')
    state = ProxyProperty('state')
    api = ProxyProperty('api')
    @property
    def threshold_messages_max(self):
        return self._object.threshold_messages_max

    @threshold_messages_max.setter
    def threshold_messages_max(self, value):
        if value is None or value is '':
            self._object.threshold_messages_max = None
        else:
            self._object.threshold_messages_max = int(value)

    @property
    @info
    def rabbitmq_node(self):
        return self._object.rabbitmq_vhost().rabbitmq_node()

    @property
    @info
    def rabbitmq_vhost(self):
        return self._object.rabbitmq_vhost()
    @property
    def status(self):
	if self.state != 'running' and self.api:
		return 'Down'
	else:
		return 'Up'
