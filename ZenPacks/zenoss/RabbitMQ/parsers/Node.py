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
    def processResults(self, cmd, result):
        """
        Router method that allows this parser to be used for all rabbitmqctl
        subcommands.
        """
        if 'rabbitmqctl' not in cmd.command:
            return

        if 'status' in cmd.command:
            self.processStatusResults(cmd, result)
        elif 'list_connections' in cmd.command:
            self.processListConnectionsResults(cmd, result)

    def processStatusResults(self, cmd, result):
        eventKey = eventClassKey = 'rabbitmq_node_status'

        notfound_matcher = re.compile(r'command not found').search
        error_matcher = re.compile(r'^Error: (.+)$').search
        done_matcher = re.compile(r'\.\.\.done').search

        ok = False
        event = dict(
            component=cmd.component,
            eventClassKey=eventClassKey,
            eventKey=eventKey,
            )

        for line in cmd.result.output.split('\n'):
            if notfound_matcher(line):
                result.events.append(dict(
                    summary='command not found: rabbitmqctl',
                    severity=cmd.severity,
                    **event
                    ))

                return

            match = error_matcher(line)
            if match:
                result.events.append(dict(
                    summary=match.group(1),
                    severity=cmd.severity,
                    **event
                    ))

                return

            if done_matcher(line):
                ok = True

        if ok:
            result.events.append(dict(
                summary='node status is OK',
                severity=0,
                **event
                ))

            return

        result.events.append(dict(
            summary='node status is indeterminate',
            severity=cmd.severity,
            **event
            ))

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

        data_keys = [cmd.deviceConfig.device, cmd.component]
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
