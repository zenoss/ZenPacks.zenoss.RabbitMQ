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

from Products.ZenRRD.CommandParser import ParsedResults
from Products.ZenRRD.zencommand import Cmd, DataPointConfig
from Products.ZenTestCase.BaseTestCase import BaseTestCase

from ..parsers.RabbitMQCTL import RabbitMQCTL as RabbitMQCTLParser

from .util import loadData


class FakeCmdResult(object):
    exitCode = None
    output = None

    def __init__(self, exitCode, output):
        self.exitCode = exitCode
        self.output = output


class TestParser(BaseTestCase):
    def _getCmd(self, component, command, exitCode, output_filename, points):
        cmd = Cmd()

        # DeviceConfig no longer exists as of Zenoss 4.
        try:
            from Products.ZenRRD.zencommand import DeviceConfig
            cmd.deviceConfig = DeviceConfig()
        except ImportError:
            from Products.ZenCollector.services.config import DeviceProxy
            cmd.deviceConfig = DeviceProxy()

        cmd.deviceConfig.device = 'maverick'
        cmd.component = component
        cmd.command = command
        cmd.eventClass = '/Status/RabbitMQ'
        cmd.eventKey = 'rabbitmq_node_status'
        cmd.result = FakeCmdResult(exitCode, loadData(output_filename))
        cmd.points = points

        return cmd

    def _getListChannelsCmd(self, exitCode, output_filename):
        points = []
        for dp_id in ('consumers', 'unacknowledged', 'uncommitted'):
            dpc = DataPointConfig()
            dpc.id = dp_id
            dpc.component = 'rabbit@maverick'
            points.append(dpc)

        cmd = self._getCmd(
            'rabbit@maverick',
            'rabbitmqctl -q -n rabbit@maverick list_channels pid consumer_count messages_unacknowledged acks_uncommitted status 2>&1',
            exitCode, output_filename, points)

        return cmd

    def testListChannels(self):
        parser = RabbitMQCTLParser()
        results = ParsedResults()
        parser.processResults(
            self._getListChannelsCmd(0, 'cmd_list_channels.txt'),
            results)

        self.assertEquals(len(results.values), 3)
        self.assertEquals(len(results.events), 1)

    def testListChannels_none(self):
        parser = RabbitMQCTLParser()
        results = ParsedResults()
        parser.processResults(
            self._getListChannelsCmd(0, 'cmd_list_channels_none.txt'),
            results)

        self.assertEquals(len(results.values), 3)
        self.assertEquals(len(results.events), 1)

    def testListChannels_notRunning(self):
        parser = RabbitMQCTLParser()
        results = ParsedResults()
        parser.processResults(
            self._getListChannelsCmd(2, 'cmd_list_channels_not_running.txt'),
            results)

        self.assertEquals(len(results.values), 0)
        self.assertEquals(len(results.events), 1)

    def _getListConnectionsCmd(self, exitCode, output_filename):
        points = []

        fields = (
            'connections', 'channels', 'sendQueue', 'recvBytes', 'recvCount',
            'sendBytes', 'sendCount',
            )

        for dp_id in fields:
            dpc = DataPointConfig()
            dpc.id = dp_id
            dpc.component = 'rabbit@maverick'
            points.append(dpc)

        cmd = self._getCmd(
            'rabbit@maverick',
            'rabbitmqctl -q -n rabbit@maverick list_connections pid channels recv_oct recv_cnt send_oct send_cnt send_pend status 2>&1',
            exitCode, output_filename, points)
        return cmd

    def testListConnections(self):
        parser = RabbitMQCTLParser()
        results = ParsedResults()
        parser.processResults(
            self._getListConnectionsCmd(0, 'cmd_list_connections.txt'),
            results)

        self.assertEquals(len(results.values), 7)
        self.assertEquals(len(results.events), 1)

    def testListConnections_none(self):
        parser = RabbitMQCTLParser()
        results = ParsedResults()

        parser.processResults(
            self._getListConnectionsCmd(0, 'cmd_list_connections_none.txt'),
            results)

        self.assertEquals(len(results.values), 7)
        self.assertEquals(len(results.events), 1)

    def testListConnections_notRunning(self):
        parser = RabbitMQCTLParser()
        results = ParsedResults()
        parser.processResults(
            self._getListConnectionsCmd(2, 'cmd_list_connections_not_running.txt'),
            results)

        self.assertEquals(len(results.values), 0)
        self.assertEquals(len(results.events), 1)

    def _getListQueuesCmd(self, exitCode, output_filename):
        points = []

        components = (
            'zenoss.queues.modelrequests.vmware',
            'zenoss.queues.zep.migrated.summary',
            'zenoss.queues.zep.migrated.archive',
            'zenoss.queues.zep.rawevents',
            'zenoss.queues.dsa.impactchange',
            'zenoss.queues.zep.heartbeats',
            'zenoss.queues.state.zenevents',
            'zenoss.queues.dsa.statechange',
            'zenoss.queues.zep.zenevents',
            'zenoss.queues.zep.modelchange',
            'zenoss.queues.impact.modelchange',
            )

        fields = (
            'ready', 'unacknowledged', 'messages', 'consumers', 'memory',
            )

        for component in components:
            for dp_id in fields:
                dpc = DataPointConfig()
                dpc.id = dp_id
                dpc.component = component
                points.append(dpc)

        cmd = self._getCmd(
            'rabbit@maverick',
            'rabbitmqctl -q -n rabbit@dev1 list_queues -p /zenoss name messages_ready messages_unacknowledged messages consumers memory status 2>&1',
            exitCode, output_filename, points)

        return cmd

    def testListQueues(self):
        parser = RabbitMQCTLParser()
        results = ParsedResults()

        parser.processResults(
            self._getListQueuesCmd(0, 'cmd_list_queues.txt'),
            results)

        self.assertEquals(len(results.values), 55)
        self.assertEquals(len(results.events), 1)

    def testListQueues_none(self):
        parser = RabbitMQCTLParser()
        results = ParsedResults()

        parser.processResults(
            self._getListQueuesCmd(0, 'cmd_list_queues_none.txt'),
            results)

        self.assertEquals(len(results.values), 0)
        self.assertEquals(len(results.events), 1)

    def testListQueues_notRunning(self):
        parser = RabbitMQCTLParser()
        results = ParsedResults()

        parser.processResults(
            self._getListQueuesCmd(2, 'cmd_list_queues_not_running.txt'),
            results)

        self.assertEquals(len(results.values), 0)
        self.assertEquals(len(results.events), 1)

    def _getStatusCmd(self, exitCode, output_filename):
        cmd = self._getCmd(
            'rabbit@maverick',
            'rabbitmqctl -q -n ${here/title} status 2>&1',
            exitCode, output_filename, [])

        return cmd

    def testStatus(self):
        parser = RabbitMQCTLParser()
        results = ParsedResults()
        parser.processResults(
            self._getStatusCmd(0, 'cmd_status.txt'),
            results)

        self.assertEquals(len(results.values), 0)
        self.assertEquals(len(results.events), 1)

    def testStatus_notRunning(self):
        parser = RabbitMQCTLParser()
        results = ParsedResults()
        parser.processResults(
            self._getStatusCmd(2, 'cmd_status_not_running.txt'),
            results)

        self.assertEquals(len(results.values), 0)
        self.assertEquals(len(results.events), 1)

    def testStatus_noRabbitMQCTL(self):
        parser = RabbitMQCTLParser()
        results = ParsedResults()
        parser.processResults(
            self._getStatusCmd(2, 'cmd_status_no_rabbitmqctl.txt'),
            results)

        self.assertEquals(len(results.values), 0)
        self.assertEquals(len(results.events), 1)

    def testStatus_unknownError(self):
        parser = RabbitMQCTLParser()
        results = ParsedResults()
        parser.processResults(
            self._getStatusCmd(2, 'cmd_status_unknown_error.txt'),
            results)

        self.assertEquals(len(results.values), 0)
        self.assertEquals(len(results.events), 1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestParser))
    return suite
