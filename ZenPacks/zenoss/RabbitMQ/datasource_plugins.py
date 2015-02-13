import time
from Products.ZenEvents import ZenEventClasses
from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
	import PythonDataSourcePlugin
from twisted.internet import defer
from twisted.internet.defer import DeferredList
from twisted.web.client import getPage
from twisted.web.error import Error
from base64 import b64encode
import json
import logging

LOG = logging.getLogger('zen.RabbitMQ')

from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId


class RabbitMQDS(PythonDataSourcePlugin):
    proxy_attributes = (
		'zRabbitMQAdminPassword',
		'zRabbitMQAdminUser',
		'zRabbitMQAPIPort',
		)
    def __init__(self):
	self.data = {}
	self.events = []
	self.values ={}
	self.maps=[]
	self.error=False
	self.sev=0

    @classmethod
    def config_key(cls, datasource, context):
		"""
		Return a tuple defining collection uniqueness.
 
		This is a classmethod that is executed in zenhub. The datasource and
		context parameters are the full objects.
 
		This example implementation is the default. Split configurations by
		device, cycle time, template id, datasource id and the Python data
		source's plugin class name.
 
		You can omit this method from your implementation entirely if this
		default uniqueness behavior fits your needs. In many cases it will.
		"""
		return (
			context.device().id,
			datasource.getCycleTime(context),
			datasource.rrdTemplate().id,
			datasource.id,
			datasource.plugin_classname,
			)
 
    @classmethod
    def params(cls, datasource, context):
		"""
		Return params dictionary needed for this plugin.
 
		This is a classmethod that is executed in zenhub. The datasource and
		context parameters are the full objects.
 
		This example implementation will provide no extra information for
		each data source to the collect method.
 
		You can omit this method from your implementation if you don't require
		any additional information on each of the datasources of the config
		parameter to the collect method below. If you only need extra
		information at the device level it is easier to just use
		proxy_attributes as mentioned above.
		"""
		comps={}
		for comp in context.getDeviceComponents():
			if comps.has_key(comp.meta_type):
				comps[comp.meta_type][comp.name()] =  0
			else:
				comps[comp.meta_type] = {}
			
		return comps

    def makeEvent(self,summary,severity,key,component,eclass="/Unknown",message=""):
		if message == "":
			message=summary	
		return {
				'summary': summary,
				'eventKey': key ,
				'severity': severity,
				'component': component,
				'eventClass': eclass,
				'message': message,
		}

    def combine(self,results,point):
        self.data[point] = json.loads(results)
	
    def errBack(self,results,dev,page):
		self.error=True
		LOG.error("error")
		return None
    def collect(self,config):
	"""
	No default collect behavior. You must implement this method.

	This method must return a Twisted deferred. The deferred results will
	be sent to the onResult then either onSuccess or onError callbacks
	below.
	"""
	device = config.datasources[0]
	deferreds=[]
	self.page='http://%s:%s/api/' %(device.device,str(device.zRabbitMQAPIPort))
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
                
        dl=DeferredList(defList,consumeErrors=True)
	dl.addCallback(self.listCall,self.page)
	
	return dl
    def listCall(self,results,page):
	#import pdb;pdb.set_trace()
	for success,result in results:
		if not success:
			if result.value[0] == '401':
				sev=ZenEventClasses.Info
			else: 
				self.sev=5
				sev = ZenEventClasses.Critical
			self.events.append(self.makeEvent("Error accessing %s" % (page),sev,"RabbitMQDown",'',"/Status/RabbitMQ",result.getErrorMessage()))
			self.error=True
			return None
    def onSuccess(self, results, config):

        maps = []

        node_title = None
        node_id = None
        nodes = []
	maps1 = []
	device = config.datasources[0]
	comps= config.datasources[0].params
	if self.error:
		myresult = {'events':self.events,}
		return myresult
        for node in self.data['nodes']: 
		if node['running']:
			node_title = node['name']
			node_id = prepId(node_title)

            		LOG.info('Found node %s on %s', node_title, device.device)


        		# vhosts
			vhosts=self.getVHostRelMap(
            			device,'rabbitmq_apinodes/%s' % node_id,node_title,comps)
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
       		self.maps =  maps
	clearEvent = {
                	'summary': 'successful collection',
                	'eventKey': 'RabbitMQDown',
			'eventClass':'/Status/RabbitMQ',
                	'severity': ZenEventClasses.Clear,
        }	
	if not self.error:
		self.events.append(clearEvent)
	myresult = {'events':self.events,'maps':self.maps,}
	return myresult

    def getVHostRelMap(self, device,  compname,node,comps):
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
			for map in queues.maps:
				if comps.has_key('RabbitRabbitMQAPIQueue'):
					if comps['RabbitMQAPIQueue'].has_key(map.id):
						comps['RabbitMQAPIQueue'].pop(map.id)
			if comps.has_key('RabbitRabbitMQAPIQueue'):
				for queue in comps['RabbitMQAPIQueue']:
					sev = ZenEventClasses.Critical
					self.events.append(self.makeEvent("Missing queue %s" % (queue),sev,"RabbitMQQueueMissing",queue,"/Status/RabbitMQ",""))	
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
				state= 'running'

            		object_maps.append(ObjectMap(data={
                		'id': prepId(name),
		                'title': name,
		                'durable': durable,
                		'auto_delete': auto_delete,
                		'arguments': str(arguments),
				'state':state,
				'api':True,
				'modelerLock':1,
                	}))
			if state != 'running':
				self.events.append(self.makeEvent("Queue %s is down!" % (name),ZenEventClasses.Critical,"RabbitMQQueueDown",name,"/Status/RabbitMQ"))
			else:
				self.events.append(self.makeEvent("Queue %s is down!" % (name),ZenEventClasses.Clear,"RabbitMQQueueDown",name,"/Status/RabbitMQ"))
        return RelationshipMap(
            compname=compname,
            relname='rabbitmq_apiqueues',
            modname='ZenPacks.zenoss.RabbitMQ.RabbitMQAPIQueue',
            objmaps=object_maps)

    def onError(self, result, config):
		"""
		Called only on error. After onResult, before onComplete.
 
		You can omit this method if you want the error result of the collect
		method to be used without further processing. It recommended to
		implement this method to capture errors.
		"""
		return {
			'events': [{
				'summary': 'error: %s' % result,
				'eventKey': 'RabbitMQ Error',
				'severity': 4,
				}],
			}
    def cleanup(self, config):
		"""
		Called when collector exits, or task is deleted or changed.
		"""
		return
