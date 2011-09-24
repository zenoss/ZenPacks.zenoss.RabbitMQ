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

import json
import md5
import os
import re
import tempfile
import time

from Products.ZenRRD.CommandParser import CommandParser


def getTempFilename(keys):
    return os.path.join(
        tempfile.gettempdir(),
        '.zenoss_rabbitmq_%s' % md5.md5('+'.join(keys)).hexdigest())


def saveData(keys, data):
    tmpfile = getTempFilename(keys)
    tmp = open(tmpfile, 'w')
    json.dump(data, tmp)
    tmp.close()


def loadData(keys, expiration=1800):
    tmpfile = getTempFilename(keys)
    if not os.path.isfile(tmpfile):
        return None

    # Make sure temporary data isn't too stale.
    if os.stat(tmpfile).st_mtime < (time.time() - expiration):
        os.unlink(tmpfile)
        return None

    tmp = open(tmpfile, 'r')
    data = json.load(tmp)
    tmp.close()

    return data


class Node(CommandParser):
    eventKey = eventClassKey = 'rabbitmq_node_status'

    event = None

    def processResults(self, cmd, result):
        """
        Router method that allows this parser to be used for all rabbitmqctl
        subcommands.
        """
        if 'rabbitmqctl' not in cmd.command:
            return

        # Get as much error handling out of the way right away.
        if self.isError(cmd, result):
            return

        # Route to the right parser based on the command.
        if 'status' in cmd.command:
            self.processStatusResults(cmd, result)
        elif 'list_connections' in cmd.command:
            self.processListConnectionsResults(cmd, result)
        elif 'list_channels' in cmd.command:
            self.processListChannelsResults(cmd, result)
        elif 'list_queues' in cmd.command:
            self.processListQueuesResults(cmd, result)

    def processStatusResults(self, cmd, result):
        result.events.append(self.getEvent(
            cmd, "node status is OK", clear=True))

    def processListConnectionsResults(self, cmd, result):
        connections = {}

        for line in cmd.result.output.split('\n'):
            if not line:
                continue

            fields = re.split(r'\s+', line.rstrip())

            # pid, channels, recv_oct, recv_cnt, send_oct, send_cnt, send_pend
            if len(fields) != 7:
                return

            connections[fields[0]] = dict(
                channels=int(fields[1]),
                recvBytes=int(fields[2]),
                recvCount=int(fields[3]),
                sendBytes=int(fields[4]),
                sendCount=int(fields[5]),
                sendQueue=int(fields[6]),
                )

        if len(connections.keys()) < 1:
            return

        dp_map = dict([(dp.id, dp) for dp in cmd.points])

        # Metrics that don't require getting a difference since the last
        # collection.
        if 'connections' in dp_map:
            result.values.append((
                dp_map['connections'], len(connections.keys())))

        if 'channels' in dp_map:
            result.values.append((dp_map['channels'], reduce(
                lambda x, y: x + y,
                (x['channels'] for x in connections.values()))))

        if 'sendQueue' in dp_map:
            result.values.append((dp_map['sendQueue'], reduce(
                lambda x, y: x + y,
                (x['sendQueue'] for x in connections.values()))))

        # For metrics that require getting a difference since the last
        # collection we need to break it down by individual connection.
        # Otherwise we'd get bad data as connections come and go.
        deltas = {}
        delta_fields = ('recvBytes', 'recvCount', 'sendBytes', 'sendCount')
        for field in delta_fields:
            deltas[field] = 0

        data_keys = [cmd.deviceConfig.device, cmd.component, 'connections']
        old = loadData(data_keys) or {}
        saveData(data_keys, connections)

        # Start by calculating deltas for PIDs that have a previous value.
        for pid in set(connections.keys()) & set(old.keys()):
            for field in delta_fields:
                delta = connections[pid][field] - old[pid][field]
                if delta < 0:
                    delta = connections[pid][field]

                deltas[field] += delta

        # For new PIDs we can use the current value as the delta.
        for pid in set(connections.keys()) - set(old.keys()):
            for field in delta_fields:
                deltas[field] += connections[pid][field]

        for field in delta_fields:
            if field in dp_map:
                result.values.append((
                    dp_map[field], deltas[field]))

    def processListChannelsResults(self, cmd, result):
        channels = {}

        for line in cmd.result.output.split('\n'):
            if not line:
                continue

            fields = re.split(r'\s+', line.rstrip())

            # pid consumer_count messages_unacknowledged acks_uncommitted
            if len(fields) != 4:
                return

            channels[fields[0]] = dict(
                consumers=int(fields[1]),
                unacknowledged=int(fields[2]),
                uncommitted=int(fields[3]),
                )

        if len(channels.keys()) < 1:
            return

        dp_map = dict([(dp.id, dp) for dp in cmd.points])

        if 'consumers' in dp_map:
            result.values.append((dp_map['consumers'], reduce(
                lambda x, y: x + y,
                (x['consumers'] for x in channels.values()))))

        if 'unacknowledged' in dp_map:
            result.values.append((dp_map['unacknowledged'], reduce(
                lambda x, y: x + y,
                (x['unacknowledged'] for x in channels.values()))))

        if 'uncommitted' in dp_map:
            result.values.append((dp_map['uncommitted'], reduce(
                lambda x, y: x + y,
                (x['uncommitted'] for x in channels.values()))))

    def processListQueuesResults(self, cmd, result):
        queues = {}

        for line in cmd.result.output.split('\n'):
            if not line:
                continue

            fields = re.split(r'\s+', line.rstrip())

            # name messages_ready messages_unacknowledged messages consumers
            # memory
            if len(fields) != 6:
                return

            queues[fields[0]] = dict(
                ready=int(fields[1]),
                unacknowledged=int(fields[2]),
                messages=int(fields[3]),
                consumers=int(fields[4]),
                memory=int(fields[5]),
                )

        if len(queues.keys()) < 1:
            return

        dp_map = dict([(dp.id, dp) for dp in cmd.points])

        if cmd.component not in queues:
            return

        for field in (
            'ready', 'unacknowledged', 'messages', 'consumers', 'memory'):

            if field in dp_map:
                result.values.append((
                    dp_map[field], queues[cmd.component][field]))

    def isError(self, cmd, result):
        match = re.search(r'^Error: (.+)$', cmd.result.output, re.MULTILINE)
        if match:
            result.events.append(self.getEvent(
                cmd, match.group(1),
                message=cmd.result.output))

            return True

        match = re.search(r'command not found', cmd.result.output, re.MULTILINE)
        if match:
            result.events.append(self.getEvent(
                cmd, "command not found: rabbitmqctl",
                message=cmd.result.output))

            return True

        if cmd.result.exitCode != 0:
            result.events.append(self.getEvent(
                cmd, "rabbitmqctl error - see event message",
                message=cmd.result.output))

            return True

        return False

    def getEvent(self, cmd, summary, message=None, clear=False):
        event = dict(
            summary=summary,
            component=cmd.component,
            eventKey=self.eventKey,
            eventClassKey=self.eventClassKey,
            )

        if message:
            event['message'] = message

        if clear:
            event['severity'] = 0
        else:
            event['severity'] = cmd.severity

        return event
