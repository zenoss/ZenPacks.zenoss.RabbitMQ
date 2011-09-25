###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011 TELUS
#
###########################################################################

from Products.Five import zcml

from Products.DataCollector.ApplyDataMap import ApplyDataMap
from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.ZenUtils.Utils import unused


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
