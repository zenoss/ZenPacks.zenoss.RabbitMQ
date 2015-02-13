#!/opt/zenoss/bin/zendmd
from twisted.web.client import getPage
from twisted.internet import reactor
from twisted.web.error import Error
from twisted.internet.defer import DeferredList
from sys import argv
from base64 import b64encode
import json

import logging
LOG = logging.getLogger('zen.RabbitMQ')

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId


class RabbitMQ(PythonPlugin):
    deviceProperties = PythonPlugin.deviceProperties + (
		'zRabbitMQAdminPassword',
		'zRabbitMQAdminUser',
		'zRabbitMQAPIPort',
		)
    def __init__(self):
	self.data = {}
    def combine(self,results,point):
        self.data[point] = json.loads(results)
	
    def collect(self,device,unused):
	self.page='http://%s:%s/api/' %(device.id,str(device.zRabbitMQAPIPort))
	if not device.zRabbitMQAdminPassword or not device.zRabbitMQAdminUser:
		LOG.info('Rabbit MQ Auth not set')
		auth = None
	else:
		auth = "Basic " +b64encode(device.zRabbitMQAdminUser+":"+device.zRabbitMQAdminPassword)
	defList=[]
        for point in ('nodes','vhosts','queues','exchanges'):
                if not auth:
                        # We apparently don't need authentication for this
                        d1 = getPage(self.page)
                else:
                 # We have our login information
                        d1 = getPage(self.page+point, headers={"Authorization": auth})

                d1.addCallback(self.combine,point)
                defList.append(d1)
                #d1.addErrback(self.errorHandler)
        dl=DeferredList(defList)
	return dl

    def process(self, device, results, unused):

        maps = []

        node_title = None
        node_id = None
        nodes = []
	maps1 = []
        for node in self.data['nodes']: 
		if node['running']:
			node_title = node['name']
			node_id = prepId(node_title)

            		LOG.info('Found node %s on %s', node_title, device.id)


        		# vhosts
			vhosts=self.getVHostRelMap(
            			device,'rabbitmq_apinodes/%s' % node_id,node_title)
			if vhosts:
				nodes.append(ObjectMap(data={
				'id': node_id,
				'title': node_title,
				}))
        			maps.extend(vhosts)
	if len(maps) > 0:
		maps.append(RelationshipMap(
            			relname='rabbitmq_apinodes',
            			modname='ZenPacks.zenoss.RabbitMQ.RabbitMQNodeAPI',
            			objmaps=nodes))
       		return maps
	else:
		return None

    def getVHostRelMap(self, device,  compname,node):
        rel_maps = []
        object_maps = []
	noq = False
	for vhost in self.data['vhosts']:	
                vhost_title = vhost['name']
                vhost_id = prepId(vhost_title)

                object_maps.append(ObjectMap(data={
                    'id': vhost_id,
                    'title': vhost_title,
                    }))

        	exchanges=self.getExchangeRelMap(device,'%s/rabbitmq_vhosts/%s' % (compname, vhost_id),vhost_title,node)
        	queues=self.getQueueRelMap(device,'%s/rabbitmq_vhosts/%s' % (compname, vhost_id),vhost_title,node)
		
		if len(queues.maps) == 0:
			noq = True
		else:
			noq = False	
            	   	rel_maps.append(exchanges)
        	       	rel_maps.append(queues)
	if noq:
		return None
        return [RelationshipMap(
            compname=compname,
            relname='rabbitmq_vhosts',
            modname='ZenPacks.zenoss.RabbitMQ.RabbitMQVHost',
            objmaps=object_maps)] + rel_maps

    def getExchangeRelMap(self, device, compname,vhost,node):
        object_maps = []
	for exchange in self.data['exchanges']:
	    if exchange['vhost'] == vhost:
		name = exchange['name']
		exchange_type = exchange['type']
		durable = exchange['durable']
		auto_delete = exchange['auto_delete']
		arguments = str(exchange['arguments'])

            	if not name:
                	name = 'amq.default'

	        object_maps.append(ObjectMap(data={
     			'id': prepId(name),
        	        'title': name,
       	        	'exchange_type': exchange_type,
	                'durable': durable,
        	        'auto_delete': auto_delete,
                	'arguments': arguments,
                	}))

        return RelationshipMap(
            compname=compname,
            relname='rabbitmq_exchanges',
            modname='ZenPacks.zenoss.RabbitMQ.RabbitMQExchange',
            objmaps=object_maps)

    def getQueueRelMap(self, device, compname,vhost,node):
        object_maps = []
        for queue in self.data['queues']:
		if queue['vhost'] == vhost and queue['node'] == node:
			name = queue['name']
			durable = queue['durable']
			auto_delete = queue['auto_delete']
			arguments = queue['arguments']
			try:
				state = queue['state']
			except:
				state = 'running'

            		object_maps.append(ObjectMap(data={
                		'id': prepId(name),
		                'title': name,
		                'durable': durable,
                		'auto_delete': auto_delete,
                		'arguments': str(arguments),
				'state':state,
				'api':True,
				'modelerLock':1
                	}))

        return RelationshipMap(
            compname=compname,
            relname='rabbitmq_apiqueues',
            modname='ZenPacks.zenoss.RabbitMQ.RabbitMQAPIQueue',
            objmaps=object_maps)
