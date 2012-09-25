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
log = logging.getLogger('zen.RabbitMQ')

from transaction._transaction import Transaction
from Products.Five import zcml

from Products.DataCollector.ApplyDataMap import ApplyDataMap
from Products.ZenModel import ZVersion
from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.Zuul.interfaces.info import IInfo

from ..modeler.plugins.zenoss.ssh.RabbitMQ import RabbitMQ as RabbitMQModeler

from .util import loadData


class MockJar(object):
    """Mock object for x._p_jar.

    Used to trick ApplyDataMap into not aborting transactions after adding
    non-persistent objects. Without doing this, all sub-components will cause
    ugly tracebacks in modeling tests.

    """

    def sync(self):
        pass


class TestModel(BaseTestCase):
    def afterSetUp(self):
        super(TestModel, self).afterSetUp()

        # BaseTestCast.afterSetUp already hides transaction.commit. So we also
        # need to hide transaction.abort.
        self._transaction_abort = Transaction.abort
        Transaction.abort = lambda *x: None

        self.d = self.dmd.Devices.createInstance('zenoss.RabbitMQ.testDevice')

        if not ZVersion.VERSION.startswith('3.'):
            self.d.dmd._p_jar = MockJar()

        self.applyDataMap = ApplyDataMap()._applyDataMap

        # Required to prevent erroring out when trying to define viewlets in
        # ../browser/configure.zcml.
        import zope.viewlet
        zcml.load_config('meta.zcml', zope.viewlet)

        import ZenPacks.zenoss.RabbitMQ
        zcml.load_config('configure.zcml', ZenPacks.zenoss.RabbitMQ)

    def beforeTearDown(self):
        if hasattr(self, '_transaction_abort'):
            Transaction.abort = self._transaction_abort

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
        self.assertEquals(queue.rabbitmq_node_name, 'rabbit@dev1')
        self.assertEquals(queue.rabbitmq_vhost_name, '/zenoss')

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
