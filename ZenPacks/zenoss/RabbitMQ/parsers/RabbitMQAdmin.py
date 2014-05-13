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
import logging

from Products.ZenRRD.CommandParser import CommandParser

log = logging.getLogger('zen.RabbitMQ')

class RabbitMQAdmin(CommandParser):
    createDefaultEventUsingExitCode = False

    eventKey = eventClassKey = 'rabbitmqadmin_status'

    event = None

    def processResults(self, cmd, result):
        """
        Router method that allows this parser to be used for all rabbitmqadmin subcommands.
        """
        if 'rabbitmqadmin' not in cmd.command:
            return

        # Check to make sure rabbitmqadmin was present and returned a version string
        if not self.verifyResult(cmd, result):
            return

        # Route to the right parser based on the command.
        if 'publish_details.rate' in cmd.command:
            self.processFlowRates(cmd, result)

    def processFlowRates(self, cmd, result):
        queues = {}

        for line in cmd.result.output.split('\n'):
            if not line:
                continue

            fields = re.split(r'\s+', line.rstrip())

            # name   message_stats.publish_details.rate   message_stats.deliver_get_details.rate
            if fields == ['name', 'message_stats.publish_details.rate', 'message_stats.deliver_get_details.rate']:
                continue
            elif len(fields) == 1:
                queues[fields[0]] = dict(incoming_rate=0.0, outgoing_rate=0.0) 
            elif len(fields) == 3:
                queues[fields[0]] = dict(
                    incoming_rate=float(fields[1]),
                    outgoing_rate=float(fields[2])
                    )
            else:
                continue

        if len(queues.keys()) < 1:
            return

        metrics = ( 'incoming_rate', 'outgoing_rate', )

        for point in cmd.points:
            if point.component in queues and point.id in metrics:
                result.values.append((
                    point, queues[point.component][point.id]))


    def verifyResult(self, cmd, result):
        clear = False

        rabbitmqversion_result = cmd.result.output.split('\n')[0]

        summary = 'unspecified rabbitmqadmin error'
        message = 'rabbitmqadmin command returned unexpected data: %s' % (cmd.result.output)

        match = re.search(r'No such file or directory', rabbitmqversion_result)
        if match:
            summary = 'rabbitmqadmin command not found - unable to query RabbitMQ queue rates'
            message = 'Please refer to http://wiki.zenoss.org/ZenPack:RabbitMQ for setup instructions.'
            clear = False
        else:
             match = re.search(r'rabbitmqadmin \d\.\d', rabbitmqversion_result)
             # In RabbitMQ version 3.1.x and later, --version was added
             if match:
                 summary = 'rabbitmqadmin status is OK'
                 message = '%s is available' % (rabbitmqversion_result)
                 clear = True
             match = re.search(r'Usage', rabbitmqversion_result)
             # In RabbitMQ version 2.8.x through 3.0.x, , --version not present, you get usage
             if match:
                 summary = 'rabbitmqadmin status is OK'
                 message = '%s is available' % (rabbitmqversion_result)
                 clear = True

        result.events.append(self.getEvent(cmd, summary, message, clear=clear))

        return clear

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
