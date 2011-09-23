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

import re

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId


class RabbitMQ(CommandPlugin):
    command = (
        'rabbitmqctl status ; '
        'echo __COMMAND__ ; '
        'for vhost in $(rabbitmqctl -q list_vhosts) ; do '
        'echo "VHOST: $vhost" ; '
        'echo "__SPLIT__" ; '
        'rabbitmqctl -q list_exchanges -p $vhost '
        'name type durable auto_delete arguments ; '
        'echo "__SPLIT__" ; '
        'rabbitmqctl -q list_queues -p $vhost '
        'name durable auto_delete arguments ; '
        'echo "__VHOST__" ; '
        'done'
        )

    def process(self, device, results, log):
        log.info('Collecting RabbitMQ data for device %s', device.id)

        status_string, vhosts_string = results.split('__COMMAND__')

        maps = []

        # nodes - only one for now
        node_id = None
        nodes = []
        for line in status_string.split('\n'):
            match = re.search(r'Status of node (\S+)\s', line)
            if match:
                node_id = prepId(match.group(1))
                nodes.append(ObjectMap(data={
                    'id': node_id,
                    'title': match.group(1),
                    }))

                break

        if len(nodes) < 1:
            return None

        maps.append(RelationshipMap(
            relname='rabbitmq_nodes',
            modname='ZenPacks.zenoss.RabbitMQ.RabbitMQNode',
            objmaps=nodes))

        # vhosts
        maps.extend(self.getVHostRelMap(
            vhosts_string, 'rabbitmq_nodes/%s' % node_id))

        import pdb; pdb.set_trace()
        return maps

    def getVHostRelMap(self, vhosts_string, compname):
        rel_maps = []
        object_maps = []

        for vhost_string in vhosts_string.split('__VHOST__'):
            if not vhost_string.strip():
                continue

            name_string, exchanges_string, queues_string = \
                vhost_string.split('__SPLIT__')

            match = re.search('VHOST:\s+(.+)$', name_string)
            if match:
                vhost_id = prepId(match.group(1))
                object_maps.append(ObjectMap(data={
                    'id': vhost_id,
                    'title': match.group(1),
                    }))

                rel_maps.extend(self.getExchangeRelMap(exchanges_string,
                    '%s/rabbitmq_vhosts/%s' % (compname, vhost_id)))

                rel_maps.extend(self.getQueueRelMap(queues_string,
                    '%s/rabbitmq_vhosts/%s' % (compname, vhost_id)))

        return [RelationshipMap(
            compname=compname,
            relname='rabbitmq_vhosts',
            modname='ZenPacks.zenoss.RabbitMQ.RabbitMQVHost',
            objmaps=object_maps)] + rel_maps

    def getExchangeRelMap(self, exchanges_string, compname):
        object_maps = []
        for exchange_string in exchanges_string.split('\n'):
            if not exchange_string.strip():
                continue

            name, exchange_type, durable, auto_delete, arguments = \
                re.split(r'\s+', exchange_string)

            if not name:
                name = 'amq.default'

            object_maps.append(ObjectMap(data={
                'id': prepId(name),
                'title': name,
                'exchange_type': exchange_type,
                'durable': durable,
                'auto_delete': auto_delete,
                'arguments': arguments,
                }))

        return [RelationshipMap(
            compname=compname,
            relname='rabbitmq_exchanges',
            modname='ZenPacks.zenoss.RabbitMQ.RabbitMQExchange',
            objmaps=object_maps)]

    def getQueueRelMap(self, queues_string, compname):
        object_maps = []
        for queue_string in queues_string.split('\n'):
            if not queue_string.strip():
                continue

            name, durable, auto_delete, arguments = \
                re.split(r'\s+', queue_string)

            object_maps.append(ObjectMap(data={
                'id': prepId(name),
                'title': name,
                'durable': durable,
                'auto_delete': auto_delete,
                'arguments': arguments,
                }))

        return [RelationshipMap(
            compname=compname,
            relname='rabbitmq_queues',
            modname='ZenPacks.zenoss.RabbitMQ.RabbitMQQueue',
            objmaps=object_maps)]
