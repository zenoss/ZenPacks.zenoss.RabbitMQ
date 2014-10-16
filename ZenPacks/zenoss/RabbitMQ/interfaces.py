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

from Products.Zuul.form import schema
from Products.Zuul.interfaces.component import IComponentInfo
from Products.Zuul.utils import ZuulMessageFactory as _t


# In Zenoss 3 we mistakenly mapped TextLine to Zope's multi-line text
# equivalent and Text to Zope's single-line text equivalent. This was
# backwards so we flipped their meanings in Zenoss 4. The following block of
# code allows the ZenPack to work properly in Zenoss 3 and 4.

# Until backwards compatibility with Zenoss 3 is no longer desired for your
# ZenPack it is recommended that you use "SingleLineText" and "MultiLineText"
# instead of schema.TextLine or schema.Text.
from Products.ZenModel.ZVersion import VERSION as ZENOSS_VERSION
from Products.ZenUtils.Version import Version
if Version.parse('Zenoss %s' % ZENOSS_VERSION) >= Version.parse('Zenoss 4'):
    SingleLineText = schema.TextLine
    MultiLineText = schema.Text
else:
    SingleLineText = schema.Text
    MultiLineText = schema.TextLine


class IRabbitMQNodeInfo(IComponentInfo):
    vhostCount = schema.Int(title=_t(u"VHost Count"))
    exchangeCount = schema.Int(title=_t(u"Exchange Count"))
    queueCount = schema.Int(title=_t(u"Queue Count"))


class IRabbitMQVHostInfo(IComponentInfo):
    rabbitmq_node = schema.Entity(title=_t(u"Node"))
    exchangeCount = schema.Int(title=_t(u"Exchange Count"))
    queueCount = schema.Int(title=_t(u"Queue Count"))


class IRabbitMQExchangeInfo(IComponentInfo):
    rabbitmq_node = schema.Entity(title=_t(u"Node"))
    rabbitmq_vhost = schema.Entity(title=_t(u"VHost"))
    exchange_type = SingleLineText(title=_t(u"Type"))
    durable = schema.Bool(title=_t("Durable"))
    auto_delete = schema.Bool(title=_t("Auto-Delete"))
    arguments = SingleLineText(title=_t(u"Arguments"))


class IRabbitMQQueueInfo(IComponentInfo):
    rabbitmq_node = schema.Entity(title=_t(u"Node"))
    rabbitmq_vhost = schema.Entity(title=_t(u"VHost"))
    durable = schema.Bool(title=_t("Durable"))
    auto_delete = schema.Bool(title=_t("Auto-Delete"))
    arguments = SingleLineText(title=_t(u"Arguments"))

    threshold_messages_max = schema.Int(
        title=_t(u"Threshold - Messages (Maximum)"),
        alwaysEditable=True)

class IRabbitMQQueueAPIInfo(IComponentInfo):
    rabbitmq_node = schema.Entity(title=_t(u"Node"))
    rabbitmq_vhost = schema.Entity(title=_t(u"VHost"))
    durable = schema.Bool(title=_t("Durable"))
    auto_delete = schema.Bool(title=_t("Auto-Delete"))
    arguments = SingleLineText(title=_t(u"Arguments"))
    state = SingleLineText(title=_t(u"State"))
    api = schema.Bool(title=_t("API"))

    threshold_messages_max = schema.Int(
        title=_t(u"Threshold - Messages (Maximum)"),
        alwaysEditable=True)
