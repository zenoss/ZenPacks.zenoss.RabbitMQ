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

import logging
LOG = logging.getLogger('zen.RabbitMQ')

import re

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId


class RabbitMQ(CommandPlugin):
    command = (
        'rabbitmqctl status 2>&1 && ('
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
        ')'
        )

    def process(self, device, results, unused):
        LOG.info('Trying rabbitmqctl on %s', device.id)

        # [0] == status, [1] == everything else (optional)
        command_strings = results.split('__COMMAND__')

        maps = []

        # nodes - only one for now
        node_title = None
        node_id = None
        nodes = []

        for line in command_strings[0].split('\n'):
            match = re.search(r'Status of node (\S+)\s', line)
            if match:
                node_title = match.group(1).strip("'")
                node_id = prepId(node_title)
                nodes.append(ObjectMap(data={
                    'id': node_id,
                    'title': node_title,
                    }))

                continue

            match = re.search(r'^(Error: .+)$', line)
            if match:
                LOG.info('Found node %s in error state on %s',
                    node_title, device.id)

                # We can't find enough information to knowingly update the
                # model if RabbitMQ is down.
                return None

        if len(nodes) > 0:
            LOG.info('Found node %s on %s', node_title, device.id)
        else:
            LOG.info('No node found on %s', device.id)
            return None

        maps.append(RelationshipMap(
            relname='rabbitmq_nodes',
            modname='ZenPacks.zenoss.RabbitMQ.RabbitMQNode',
            objmaps=nodes))

        # vhosts
        maps.extend(self.getVHostRelMap(
            device, command_strings[1], 'rabbitmq_nodes/%s' % node_id))

        return maps

    def getVHostRelMap(self, device, vhosts_string, compname):
        rel_maps = []
        object_maps = []

        for vhost_string in vhosts_string.split('__VHOST__'):
            if not vhost_string.strip():
                continue

            name_string, exchanges_string, queues_string = \
                vhost_string.split('__SPLIT__')

            match = re.search('VHOST:\s+(.+)$', name_string)
            if match:
                vhost_title = match.group(1)
                vhost_id = prepId(vhost_title)

                object_maps.append(ObjectMap(data={
                    'id': vhost_id,
                    'title': vhost_title,
                    }))

                exchanges = self.getExchangeRelMap(exchanges_string,
                    '%s/rabbitmq_vhosts/%s' % (compname, vhost_id))

                queues = self.getQueueRelMap(queues_string,
                    '%s/rabbitmq_vhosts/%s' % (compname, vhost_id))

                LOG.info(
                    'Found vhost %s with %d exchanges and %d queues on %s',
                    vhost_title, len(exchanges.maps), len(queues.maps),
                    device.id)

                rel_maps.append(exchanges)
                rel_maps.append(queues)

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

            if re.search(r'true', durable, re.I):
                durable = True
            else:
                durable = False

            if re.search(r'true', auto_delete, re.I):
                auto_delete = True
            else:
                auto_delete = False

            object_maps.append(ObjectMap(data={
                'id': prepId(name),
                'title': name,
                'exchange_type': exchange_type,
                'durable': durable,
                'auto_delete': auto_delete,
                'arguments': arguments,
                }))

        return RelationshipMap(
            compname=compname,
            relname='rabbitmq_exchanges',
            modname='ZenPacks.zenoss.RabbitMQ.RabbitMQExchange',
            objmaps=object_maps)

    def getQueueRelMap(self, queues_string, compname):
        object_maps = []
        for queue_string in queues_string.split('\n'):
            if not queue_string.strip():
                continue

            name, durable, auto_delete, arguments = \
                re.split(r'\s+', queue_string)

            if re.search(r'true', durable, re.I):
                durable = True
            else:
                durable = False

            if re.search(r'true', auto_delete, re.I):
                auto_delete = True
            else:
                auto_delete = False

            object_maps.append(ObjectMap(data={
                'id': prepId(name),
                'title': name,
                'durable': durable,
                'auto_delete': auto_delete,
                'arguments': arguments,
                }))

        return RelationshipMap(
            compname=compname,
            relname='rabbitmq_queues',
            modname='ZenPacks.zenoss.RabbitMQ.RabbitMQQueue',
            objmaps=object_maps)
