===============================================================================
ZenPacks.zenoss.RabbitMQ
===============================================================================

About
===============================================================================

This project is a Zenoss_ extension (ZenPack) that allows for monitoring of
RabbitMQ. See the Usage section for details on what is monitored. You can watch
the `Monitoring RabbitMQ`_ video for a quick introduction that covers most of
the details below.


Prerequisites
-------------------------------------------------------------------------------

======================  ====================================================
Prerequisite            Restriction
======================  ====================================================
Zenoss Platform         3.2 or greater
Zenoss Processes        zenmodeler, zencommand
Installed ZenPacks      ZenPacks.zenoss.RabbitMQ
Firewall Acccess        Collector server to 2/tcp of RabbitMQ server
======================  ====================================================


Related ZenPacks
-------------------------------------------------------------------------------

There already exist at least two community Zenpacks that provide monitoring for
RabbitMQ.

* *ZenPacks.dnalley.AMQPEventMonitor* by David Nalley: Very different
  functionality than what's provided by this ZenPack. It allows you to pull
  messages from a defined queue and automatically turn them into Zenoss
  events.

* *ZenPacks.community.RabbitMQ* by Greg Guthe: More similar to this
  ZenPack in its functionality. Global metrics for queued messages and rates.
  It appears to require that the HTTP management API plugin be installed into
  your RabbitMQ instances, and that a Net-SNMP extension also written by
  Greg Guthe be installed.

The major differences between the ZenPacks.community.RabbitMQ and this pack are
that this pack simply runs various rabbitmqctl commands over SSH both to model
the node, vhosts, exchanges and queues; as well as to monitor connection,
channel and per-queue metrics. So you don't need to install anything extra on
your RabbitMQ server, and you get more granularity on the monitoring.

In the future this pack might be extended to also support RabbitMQ's HTTP
management API plugin in addition to the SSH method.


Usage
===============================================================================

Installation
-------------------------------------------------------------------------------

This ZenPack has no special installation considerations. You should install the
most recent version of the ZenPack for the version of Zenoss you're running.

The ZenPack can be downloaded from `<http://zenpacks.zenoss.com/>`_.

To install the ZenPack you must copy the ``.egg`` file to your Zenoss master
server and run the following command as the ``zenoss`` user::

    zenpack --install <filename.egg>

After installing you must restart Zenoss by running the following command as
the ``zenoss`` user on your master Zenoss server::

    zenoss restart

If you have distributed collectors you must also update them after installing
the ZenPack.


Configuring
-------------------------------------------------------------------------------

Installing the ZenPack will add the following objects to your Zenoss system.

* Modeling Plugins

  * zenoss.ssh.RabbitMQ

* Monitoring Templates

  * RabbitMQNode in /Devices
  * RabbitMQQueue in /Devices

* Event Classes

  * /Status/RabbitMQ
  * /Perf/RabbitMQ

* Command Parsers

  * ZenPacks.zenoss.RabbitMQ.parsers.RabbitMQCTL

These monitoring templates should not be bound directly to any devices in the
system.

To start monitoring your RabbitMQ server you will need to setup SSH access so
that your Zenoss collector server will be able to SSH into your RabbitMQ
server(s) as a user who has permission to run the ``rabbitmqctl`` command. This
almost always means the root user. See the *Using a Non-Root User* section
below for instructions on allowing non-root users to run ``rabbitmqctl``. To do
this you need to set the following zProperties for the RabbitMQ devices or
their device class in Zenoss.

* zCommandUsername
* zCommandPassword
* zKeyPath

The zCommandUsername property must be set. To use public key authentication you
must verify that the public portion of the key referenced in zKeyPath is
installed in the `~/.ssh/authorized_keys` file for the appropriate user on the
RabbitMQ server. If this key has a passphrase you should set it in the
zCommandPassword property. If you'd rather use password authentication than
setup keys, simply put the user's password in the zCommandPassword property.

You should then add the zenoss.ssh.RabbitMQ modeler plugin to the device, or
device class containing your RabbitMQ servers and remodel the device(s). This
will automatically find the node, vhosts, exchanges and queues and begin
monitoring them immediately for the following metrics.

* Node Values

  * Status - Running or not? Generates event on failure.
  * Open Connections & Channels
  * Sent & Received Bytes Rate
  * Sent & Received Messages Rate
  * Depth of Send Queue
  * Consumers
  * Unacknowledged & Uncommitted Messages

* Queue Values

  * Ready, Unacknowledged & Total Messages
  * Memory Usage
  * Consumers

There is a default threshold of 1,000,000 messages per queue. This is almost
certainly an absurdly high threshold that shouldn't trip in normal systems.
However, by clicking into the details of any individual queue you can set the
per-queue threshold to a more reasonable value that makes sense for a given
queue.


Using a Non-Root User
-------------------------------------------------------------------------------

This ZenPack requires the ability to run the ``rabbitmqctl`` command remotely
on your RabbitMQ server(s) using SSH. By default, the ``rabbitmqctl`` command
is only allowed to be run by the *root* and *rabbitmq* users. Furthermore, this
ZenPack expects the ``rabbitmqctl`` command be in the user's path. Normally
this is only true for the root user.

.. warning::

   There's a very good reason for this restriction. Once a user is allowed to
   execute the ``rabbitmqctl`` command, they are able to perform the following
   actions.

   - Stop, Start or Reset RabbitMQ
   - Control a RabbitMQ Cluster
   - Close Open Connections
   - Manage Users and Security
   - Manage VHosts

   In a nutshell, this means that any user with permission to run
   ``rabbitmqctl`` can wreak total havoc on your RabbitMQ server if they had
   the intent to do so.


Assuming that you've created a user named *zenmonitor* on your RabbitMQ servers
for monitoring purposes, you can follow these steps to allow the *zenmonitor*
user to run ``rabbitmqctl``.

1. Install the *sudo* package on your server.

2. Make sudo not require a TTY. This allows sudo to be run via ssh.

   1. Run ``visudo`` as root.

   2. Find a line containing ``Defaults requiretty`` and comment it out by
      prefixing the line with a ``#``.

   3. Type ``ESC`` then ``:wq`` to save the sudo configuration.

3. Allow the *zenmonitor* user to run rabbitmqctl.

   1. Run ``visudo`` as root.

   2. Add the following line to the bottom of the file.

      .. sourcecode::

         zenmonitor ALL=(ALL) NOPASSWD: /usr/sbin/rabbitmqctl

   3. Type ``ESC`` then ``:wq`` to save the sudo configuration.

4. Alias rabbitmqctl for the *zenmonitor* user.

   1. Add the following lines to ``/home/zenmonitor/.bashrc``.


Screenshots
===============================================================================

* *Components*

  |Components|

* *Nodes*

  |Nodes|

* *Node Throughput*

  |Node Throughput|

* *Node Channels*

  |Node Channels|

* *VHosts*

  |VHosts|

* *Queues*

  |Queues|

* *Queue Metrics*

  |Queue Metrics|


.. _`Zenoss`: http://www.zenoss.com/
.. _`Monitoring RabbitMQ`: http://www.youtube.com/watch?v=CAak2ayFcV0

.. |Components| image:: https://github.com/zenoss/ZenPacks.zenoss.RabbitMQ/raw/master/docs/components.png
.. |Nodes| image:: https://github.com/zenoss/ZenPacks.zenoss.RabbitMQ/raw/master/docs/nodes.png
.. |Node Throughput| image:: https://github.com/zenoss/ZenPacks.zenoss.RabbitMQ/raw/master/docs/nodes_throughput.png
.. |Node Channels| image:: https://github.com/zenoss/ZenPacks.zenoss.RabbitMQ/raw/master/docs/nodes_channels.png
.. |VHosts| image:: https://github.com/zenoss/ZenPacks.zenoss.RabbitMQ/raw/master/docs/vhosts.png
.. |Exchanges| image:: https://github.com/zenoss/ZenPacks.zenoss.RabbitMQ/raw/master/docs/exchanges.png
.. |Queues| image:: https://github.com/zenoss/ZenPacks.zenoss.RabbitMQ/raw/master/docs/queues.png
.. |Queue Metrics| image:: https://github.com/zenoss/ZenPacks.zenoss.RabbitMQ/raw/master/docs/queues_metrics.png
