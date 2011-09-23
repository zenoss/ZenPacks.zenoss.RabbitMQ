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

from Products.ZenRRD.CommandParser import CommandParser


class Node(CommandParser):
    def processResults(self, cmd, result):
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
                    severity=4,
                    **event
                    ))

                return

            match = error_matcher(line)
            if match:
                result.events.append(dict(
                    summary=match.group(1),
                    severity=4,
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
            severity=4,
            **event
            ))
