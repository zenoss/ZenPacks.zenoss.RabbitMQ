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

from ..modeler.plugins.zenoss.ssh.RabbitMQ import RabbitMQ as RabbitMQModeler

from .util import loadData


class TestModeler(BaseTestCase):
    def afterSetUp(self):
        super(TestModeler, self).afterSetUp()

        self.d = self.dmd.Devices.createInstance('zenoss.RabbitMQ.testDevice')
        self.applyDataMap = ApplyDataMap()._applyDataMap

        # Required to prevent erroring out when trying to define viewlets in
        # ../browser/configure.zcml.
        import Products.ZenUI3.navigation
        zcml.load_config('testing.zcml', Products.ZenUI3.navigation)

        import ZenPacks.zenoss.RabbitMQ
        zcml.load_config('configure.zcml', ZenPacks.zenoss.RabbitMQ)

    def testRabbitMQCTLNotFound(self):
        modeler = RabbitMQModeler()
        modeler_results = loadData('model_no_rabbitmqctl.txt')
        data_maps = modeler.process(self.d, modeler_results, log)

        self.assertEquals(data_maps, None)

    def testNotRunning(self):
        modeler = RabbitMQModeler()
        modeler_results = loadData('model_not_running.txt')
        data_maps = modeler.process(self.d, modeler_results, log)

        self.assertEquals(data_maps, None)

    def testRunningZenoss(self):
        modeler = RabbitMQModeler()
        modeler_results = loadData('model_running_zenoss.txt')
        data_maps = modeler.process(self.d, modeler_results, log)

        self.assertEquals(len(data_maps), 6)

    def testRunningOpenStack(self):
        modeler = RabbitMQModeler()
        modeler_results = loadData('model_running_openstack.txt')
        data_maps = modeler.process(self.d, modeler_results, log)

        self.assertEquals(len(data_maps), 6)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestModeler))
    return suite
