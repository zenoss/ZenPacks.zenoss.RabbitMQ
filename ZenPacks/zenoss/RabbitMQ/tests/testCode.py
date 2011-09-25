###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011 TELUS
#
###########################################################################

import logging
log = logging.getLogger('zen.RabbitMQ')

import os

from Products.Five import zcml

from Products.DataCollector.ApplyDataMap import ApplyDataMap
from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.ZenUtils.Utils import unused
from Products.Zuul.interfaces.info import IInfo

from ..modeler.plugins.zenoss.ssh.RabbitMQ import RabbitMQ as RabbitMQModeler


def loadData(filename):
    f = open(os.path.join(os.path.dirname(__file__), 'data', filename), 'r')
    data = f.read()
    f.close()
    return data


class TestCode(BaseTestCase):
    def afterSetUp(self):
        super(TestCode, self).afterSetUp()

        self.d = self.dmd.Devices.createInstance('zenoss.RabbitMQ.testDevice')
        self.applyDataMap = ApplyDataMap()._applyDataMap

        if zcml._initialized:
            return

        # Required to prevent erroring out when trying to define viewlets in
        # ../browser/configure.zcml.
        import Products.ZenUI3.navigation
        zcml.load_config('testing.zcml', Products.ZenUI3.navigation)

        import ZenPacks.zenoss.RabbitMQ
        zcml.load_config('configure.zcml', ZenPacks.zenoss.RabbitMQ)

    def testModeler_rabbitmqctlNotFound(self):
        modeler = RabbitMQModeler()
        modeler_results = loadData('model_no_rabbitmqctl.txt')
        data_maps = modeler.process(self.d, modeler_results, log)

        self.assertEquals(data_maps, None)

    def testModeler_notRunning(self):
        modeler = RabbitMQModeler()
        modeler_results = loadData('model_not_running.txt')
        data_maps = modeler.process(self.d, modeler_results, log)

        self.assertEquals(data_maps, None)

    def testModeler_runningZenoss(self):
        modeler = RabbitMQModeler()
        modeler_results = loadData('model_running_zenoss.txt')
        data_maps = modeler.process(self.d, modeler_results, log)

        self.assertEquals(len(data_maps), 6)

    def testModeler_runningOpenStack(self):
        modeler = RabbitMQModeler()
        modeler_results = loadData('model_running_openstack.txt')
        data_maps = modeler.process(self.d, modeler_results, log)

        self.assertEquals(len(data_maps), 6)

    def _loadZenossData(self):
        modeler = RabbitMQModeler()
        modeler_results = loadData('model_running_zenoss.txt')

        for data_map in modeler.process(self.d, modeler_results, log):
            self.applyDataMap(self.d, data_map)

    def testRabbitMQNode(self):
        self._loadZenossData()

        self.assertEquals(self.d.rabbitmq_nodes.countObjects(), 1)

        info = IInfo(self.d.rabbitmq_nodes()[0])
        self.assertEquals(info.vhostCount, 2)
        self.assertEquals(info.exchangeCount, 23)
        self.assertEquals(info.queueCount, 11)

    def testRabbitMQVHost(self):
        self._loadZenossData()

        node = self.d.rabbitmq_nodes()[0]

        self.assertEquals(node.rabbitmq_vhosts.countObjects(), 2)

        info = IInfo(node.rabbitmq_vhosts._getOb('-'))
        self.assertEquals(info.rabbitmq_node.name, 'rabbit@dev1')
        self.assertEquals(info.exchangeCount, 7)
        self.assertEquals(info.queueCount, 0)

    def testRabbitMQExchange(self):
        self._loadZenossData()

        node = self.d.rabbitmq_nodes()[0]
        vhost = node.rabbitmq_vhosts._getOb('-')
        exchange = vhost.rabbitmq_exchanges._getOb('amq.default')

        info = IInfo(exchange)
        self.assertEquals(info.rabbitmq_node.name, 'rabbit@dev1')
        self.assertEquals(info.rabbitmq_vhost.name, '/')
        self.assertEquals(info.exchange_type, 'direct')
        self.assertTrue(info.durable is True)
        self.assertTrue(info.auto_delete is False)
        self.assertEquals(info.arguments, '[]')

    def testRabbitMQQueue(self):
        self._loadZenossData()

        node = self.d.rabbitmq_nodes()[0]
        vhost = node.rabbitmq_vhosts._getOb('zenoss')
        queue = vhost.rabbitmq_queues._getOb('zenoss.queues.zep.zenevents')

        info = IInfo(queue)
        self.assertEquals(info.rabbitmq_node.name, 'rabbit@dev1')
        self.assertEquals(info.rabbitmq_vhost.name, '/zenoss')
        self.assertTrue(info.durable is True)
        self.assertTrue(info.auto_delete is False)
        self.assertEquals(info.arguments, '[]')

    def testRabbitMQCTLParser(self):
        try:
            import ZenPacks.zenoss.RabbitMQ.parsers.RabbitMQCTL
            unused(ZenPacks.zenoss.RabbitMQ.parsers.RabbitMQCTL)
        except ImportError:
            self.assertTrue(False, "Can't import RabbitMQCTL parser")

        # Need to build a test for this. Right now it's just a TODO.
        self.assertTrue(False,
            "Channels and connections returning nothing instead of 0")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCode))
    return suite
