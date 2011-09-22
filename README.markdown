# ZenPacks.zenoss.RabbitMQ
This is a currently a work in progress. I'll update this README when there's
something worth saying in it.

## What already exists?
Why am I creating this when g-k has already created a community RabbitMQ
ZenPack?

1. I don't want to install SNMP extensions for RabbitMQ.
2. I don't want to install the HTTP API management extension for RabbitMQ.

Actually the HTTP API management extension is nice. I would like to support
them in the future to get the message rate metrics.

## What will it do?
My functionality goals are..

* Model vhosts, exchanges and queues.
* Monitor queued messages, consumers, messages and things like that.

