# ZenPacks.zenoss.RabbitMQ
This project is a [Zenoss][] extension (ZenPack) that allows for monitoring of
RabbitMQ. See the Usage section for details on what is monitored. You can watch
the [Monitoring RabbitMQ][] video for a quick introduction that covers most of
the details below.

## Requirements & Dependencies
This ZenPack is known to be compatible with Zenoss versions 3.2 through 4.0.
There's a high likelihood that it is also compatible with any Zenoss 3.0 and
3.1 also, but these have not yet been tested.

## Installation
You must first have, or install, Zenoss 3.2.0 or later. Core and Enterprise
versions are supported. You can download the free Core version of Zenoss from
<http://community.zenoss.org/community/download>.

### Normal Installation (packaged egg)
Depending on what version of Zenoss you're running you will need a different
package. Download the appropriate package for your Zenoss version from the list
below.

 * Zenoss 4.1: [Latest Package for Python 2.7][]
 * Zenoss 3.0 - 4.0: [Latest Package for Python 2.6][]

Then copy it to your Zenoss server and run the following commands as the zenoss
user.

    zenpack --install <package.egg>
    zenoss restart

### Developer Installation (link mode)
If you wish to further develop and possibly contribute back to the RabbitMQ
ZenPack you should clone the git repository, then install the ZenPack in
developer mode using the following commands.

    git clone git://github.com/zenoss/ZenPacks.zenoss.RabbitMQ.git
    zenpack --link --install ZenPacks.zenoss.RabbitMQ
    zenoss restart

## Usage
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
server(s) as a user who has permission to run the `rabbitmqctl` command. To do
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

## Related ZenPacks
There already exist at least two community Zenpacks that provide monitoring for
RabbitMQ.

 * [ZenPacks.dnalley.AMQPEventMonitor][] by [David Nalley][]: Very different
   functionality than what's provided by this ZenPack. It allows you to pull
   messages from a defined queue and automatically turn them into Zenoss
   events.
 * [ZenPacks.community.RabbitMQ][] by [Greg Guthe][]: More similar to this
   ZenPack in its functionality. Global metrics for queued messages and rates.
   It appears to require that the HTTP management API plugin be installed into
   your RabbitMQ instances, and that a Net-SNMP extension also written by
   [Greg Guthe][] be installed.

The major differences between the [ZenPacks.community.RabbitMQ][] and this pack
are that this pack simply runs various rabbitmqctl commands over SSH both to
model the node, vhosts, exchanges and queues; as well as to monitor connection,
channel and per-queue metrics. So you don't need to install anything extra on
your RabbitMQ server, and you get more granularity on the monitoring.

In the future this pack might be extended to also support RabbitMQ's HTTP
management API plugin in addition to the SSH method.

## Screenshots
![Components](https://github.com/zenoss/ZenPacks.zenoss.RabbitMQ/raw/master/docs/components.png)
![Nodes](https://github.com/zenoss/ZenPacks.zenoss.RabbitMQ/raw/master/docs/nodes.png)
![Node Throughput](https://github.com/zenoss/ZenPacks.zenoss.RabbitMQ/raw/master/docs/nodes_throughput.png)
![Node Channels](https://github.com/zenoss/ZenPacks.zenoss.RabbitMQ/raw/master/docs/nodes_channels.png)
![VHosts](https://github.com/zenoss/ZenPacks.zenoss.RabbitMQ/raw/master/docs/vhosts.png)
![Exchanges](https://github.com/zenoss/ZenPacks.zenoss.RabbitMQ/raw/master/docs/exchanges.png)
![Queues](https://github.com/zenoss/ZenPacks.zenoss.RabbitMQ/raw/master/docs/queues.png)
![Queue Metrics](https://github.com/zenoss/ZenPacks.zenoss.RabbitMQ/raw/master/docs/queues_metrics.png)


[Zenoss]: <http://www.zenoss.com/>
[Monitoring RabbitMQ]: <http://www.youtube.com/watch?v=CAak2ayFcV0>
[Latest Package for Python 2.7]: <https://github.com/downloads/zenoss/ZenPacks.zenoss.RabbitMQ/ZenPacks.zenoss.RabbitMQ-1.0.0-py2.7.egg>
[Latest Package for Python 2.6]: <https://github.com/downloads/zenoss/ZenPacks.zenoss.RabbitMQ/ZenPacks.zenoss.RabbitMQ-1.0.0-py2.6.egg>
[ZenPacks.dnalley.AMQPEventMonitor]: <http://community.zenoss.org/docs/DOC-5817>
[David Nalley]: <http://community.zenoss.org/people/ke4qqq>
[ZenPacks.community.RabbitMQ]: <https://github.com/g-k/ZenPacks.community.RabbitMQ>
[Greg Guthe]: <https://github.com/g-k>
