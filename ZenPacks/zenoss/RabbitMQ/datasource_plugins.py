from Products.ZenEvents import ZenEventClasses
from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
	import PythonDataSourcePlugin
from twisted.internet import defer
from twisted.internet.defer import DeferredList
import logging

import ZenPacks.community.NetScaler.locallibs

# Requires that locallibs first be imported.
import libNetscaler
log = logging.getLogger('zen.NetScalerDS')

class NetScalerPlugin(PythonDataSourcePlugin):
	log.debug("Starting NetScaler plugin")
	"""Explanation of what MyPlugin does."""
	client = None	
	session = None
	lbvserver_vars=['actsvcs',
		'curclntconnections',
		'cursrvrconnections',
		'deferredreq',
		'deferredreqrate',
		'establishedconn',
		'hitsrate',
		'inactsvcs',
		'invalidrequestresponse',
		'invalidrequestresponsedropped',
		'pktsrecvdrate',
		'pktssentrate',
		'requestbytesrate',
		'requestsrate',
		'responsebytesrate',
		'responsesrate',
		'totalpktsrecvd',
		'totalpktssent',
		'totalrequestbytes',
		'totalrequests',
		'totalresponsebytes',
		'totalresponses',
		'tothits',
		'totspillovers',
		'vslbhealth']
		
	# List of device attributes you'll need to do collection.
	proxy_attributes = (
		'zNetScalerUser',
		'zNetScalerPassword',
		'zNetScalerSSL',
		'zNetScalerTimeout'
		)
 
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
		return {}

	def makeEvent(self,message,severity):
		return {
			'events': [{
				'summary': message,
				'eventKey': 'NetScalerPlugin message',
				'severity': severity,
				}],
			}
	def combine(self,results):
		all_data = {}
		for success, result in results:
			if not success:
				log.error("API Error: %s", result.getErrorMessage())
			elif result:
				if all_data.has_key('values'):
					all_data['values'].update(result['values'])
				else:
					all_data.update(result)
		return all_data
	def errBack(self,result):
		log.error("error")

	def collect(self,config):
		"""
		No default collect behavior. You must implement this method.
 
		This method must return a Twisted deferred. The deferred results will
		be sent to the onResult then either onSuccess or onError callbacks
		below.
		"""
		ds0 = config.datasources[0]
		self.ip = ds0.manageIp
		deferreds=[]
		if not ds0.zNetScalerUser:
			log.error('zNetScalerUser is not set. Not discovering')
			deferreds.append(defer.maybeDeferred(self.makeEvent,'zNetScalerUser is not set. Not discovering',2))

		if not ds0.zNetScalerPassword:
			log.error('zNetScalerPassword is not set. Not discovering.')
			deferreds.append(defer.maybeDeferred(self.makeEvent,'zNetScalerPassword is not set. Not discovering',2))
		if self.client is None:
			self.client=libNetscaler.NetScalerClient(self.ip,ds0.zNetScalerUser,ds0.zNetScalerPassword,int(ds0.cycletime/4),ssl=ds0.zNetScalerSSL)
		
		if not self.client.login():
			log.error('Could not login :: ' +self.client.errMessage)
			deferreds.append(defer.maybeDeferred(self.makeEvent,'Could not login :: ' +self.client.errMessage,4))		
		else:
			log.info("Connected to %s with session %s" % (ds0.manageIp,self.client.session))
			self.session = self.client.session
			for ds in config.datasources:
				self.client.set_timeout(int(ds.cycletime/4))
				if ds.component is None:
					deferreds.append(self.client.get_component_stat('system',''))
				else:
					deferreds.append(self.client.get_component_stat('lbvserver',ds.component))
		d=DeferredList(deferreds,consumeErrors=True).addCallback(self.combine)
		return(d)

	def onSuccess(self, result, config):
		"""
		Called only on success. After onResult, before onComplete.
 
		You should return a data structure with zero or more events, values
		and maps.
		"""
		pluginResults ={}
		pluginResults['events'] = []
		pluginResults['maps'] = []
		pluginResults['values'] = None

		clearEvent = {
                	'summary': 'successful collection',
                	'eventKey': 'NetScalerPlugin OK',
                	'severity': ZenEventClasses.Clear,
                }	
		if 'events' in result:
			pluginResults['events'] = result['events'].append(clearEvent)
		else:
			pluginResults['events'].append(clearEvent)
		if 'maps' in result:	
			pluginResults['maps'] = result['maps']
		if 'values' in result:
			pluginResults['values'] = result['values']
		return pluginResults	
 
	def onError(self, result, config):
		"""
		Called only on error. After onResult, before onComplete.
 
		You can omit this method if you want the error result of the collect
		method to be used without further processing. It recommended to
		implement this method to capture errors.
		"""
		if self.client.session is not None:
			log.info("onError: logging out " + config.id)
			self.client.logout()
		return {
			'events': [{
				'summary': 'error: %s' % result,
				'eventKey': 'NetScalerPlugin Error',
				'severity': 4,
				}],
			}
	def onComplete(self,result,config):
		if self.client.session is not None:
			log.info("onComplete: logging out " + config.id)
			self.client.logout()
		return result
	def cleanup(self, config):
		"""
		Called when collector exits, or task is deleted or changed.
		"""
		if self.client is not None and self.client.session is not None:
			log.info("cleanup :: Logging out of NS " + config.id)
			self.client.logout()
		return

