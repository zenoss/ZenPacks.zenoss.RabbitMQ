###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011 TELUS
#
###########################################################################

import logging
log = logging.getLogger('zen.RabbitMQ')

from Products.Five import zcml

from Products.DataCollector.ApplyDataMap import ApplyDataMap
from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.Zuul.interfaces.info import IInfo

from ..modeler.plugins.zenoss.ssh.RabbitMQ import RabbitMQ as RabbitMQModeler

from .util import loadData


class TestModel(BaseTestCase):
    def afterSetUp(self):
        super(TestModel, self).afterSetUp()

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


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestModel))
    return suite
