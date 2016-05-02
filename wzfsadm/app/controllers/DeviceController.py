import re
from BaseController import BaseController

class DeviceController( BaseController ):
	#-------------------------------------------------------------------------#
	# Render page for adding vdevice to pool
	def addform( self, query ):

		self.template = "device_add_form.html"
		# Availiable pools to add to
		pools = []
		# We are adding to specific pool if target_pool is specified
		if "target_pool" in query:
			# Add target pool to availiable pools to add
			pools.append( query["target_pool"][0] )
		else:
			# Need to give user all avaliable pools
			module = "Pool"
			function_name = "list_zpool_names"
			# Get function from api
			loaded_module = self.model.load_module( module )			
			# Calling function list_zpool_names
			status, api_response = loaded_module.list_zpool_names()

			if not status:
				# Something in API goes wrong
				self.error_handler( api_response["response"] )
				return
			# Gather all available pools
			pools = api_response["data"]
		# We have availiable pools 
		module = "Pool"
		# Get function from api
		loaded_module = self.model.load_module( module )		
		# Calling function list_sources
		status, api_response = loaded_module.list_sources()
		if not status:
			# Somethin in API goes wrong
			self.error_handler( api_response["response"] )
			return
		# Fill template data
		# Redirect after filling form
		self.template_data["action"] = "/device/add"
		self.template_data["pools"] = pools
		self.template_data["sources"] = api_response["data"]
		self.template_data["title"] = "Add device"
		self.template_data["heading"] = "Add device"
		self.template_data["description"] = "This page let you add specific device to existing pool. You can choose from types of virtual devices like mirror, raid-z etc."
		# Set code and render template
		self.set_response_code( 200 )
		self.render_view()	
	#-------------------------------------------------------------------------#
	# Add vdev to zpool and render status page
	def add( self, query ):
		self.template = "status_page.html"
		# We dont have arguments or don't have target pool to add device
		if not query or "target_pool" not in query:
			# We dont have right arguments to complete the action
			self.error_handler( "No arguments was passed." )
			return

		module = "Device"
		# Get function from api
		loaded_module = self.model.load_module( module )
		# We are trying to call add_device( target_pool, resources, device_type, forced )
		# Need to prepare default arguments
		target_pool = query["target_pool"][0]			
		resources = {
			"files": [],
			"disks": []
		}		
		device_type = None
		forced = False
		# Gather files, partitions and disk from query
		devices = []

		if "device" in query:
			devices = query["device"]

		# Need to gather type and if command should be forced
		if "type" in query:
			device_type = query["type"][0]
		if "forced" in query:
			forced = True
		# Calling api function with apropriate parameters
		status, api_response = loaded_module.add_device( target_pool, devices, device_type, forced )

		self.template_data["actions"] = [
			{ "name":"Dashboard", "link": "/" },
			{ "name":"Modified pool <em>%s</em>" % target_pool , "link": "/zpool/detail?pool=%s" % target_pool }
		]

		if not status:
			# Something in API went wrong
			self.error_handler( api_response["response"] )
			return
		
		self.template_data["status"] = "OK"
		self.template_data["response"] = api_response["response"]
		self.template_data["title"] = "Status page"
		self.template_data["heading"] = ( "Adding device to pool <em>%s</em>" % ( target_pool ) )
		self.template_data["description"] = "Status page show result of operation. In case of success you will see green bar. Otherwise red bar."		
		# Set code and render template
		self.set_response_code( 200 )
		self.render_view()	
	#-------------------------------------------------------------------------#
	def attachform( self, query ):

		self.template = "device_attach_form.html"
		
		if not query or "target_pool" not in query or "attach_target" not in query:
			# We dont have right arguments to complete the action
			self.error_handler( "No arguments was passed." )
			return

		module = "Pool"
		loaded_module = self.model.load_module( module )
		# Get function from api
		# We have function => call it list_sources()
		status, api_response = loaded_module.list_sources()

		if not status:
		# Something in API goes wrong
			self.error_handler( api_response["response"] )
			return
		# Fill template data
		# Redirect after filling form
		self.template_data["action"] = "/device/attach"
		self.template_data["sources"] = api_response["data"]
		self.template_data["target_pool"] = query["target_pool"][0]
		self.template_data["attach_target"] = query["attach_target"][0]
		self.template_data["title"] = "Attach device"
		self.template_data["heading"] = "Attach device"
		self.template_data["description"] = "This page let you attach specific device to existing device in pool. You can choose which device you will attach from available sources."		

		self.set_response_code( 200 )
		self.render_view()

	#-------------------------------------------------------------------------#
	def attach( self, query ):
		
		self.template = "status_page.html"

		if not query or "target_pool" not in query or "attach_target" not in query or "device" not in query:
			# We dont have right arguments to complete the action
			self.error_handler( "No arguments was passed." )
			return

		module = "Device"

		loaded_module = self.model.load_module( module )
		# Get function from api		
		target_pool = query["target_pool"][0]
		attach_target = query["attach_target"][0]
		device = query["device"][0]

		status, api_response = loaded_module.device_attach( target_pool, attach_target, device )

		self.template_data["actions"] = [
			{ "name":"Dashboard", "link": "/" },
			{ "name":"Modified pool <em>%s</em>" % target_pool , "link": "/zpool/detail?pool=%s" % target_pool }
		]

		if not status:
		# Something in API goes wrong
			self.error_handler( api_response["response"] )
			return

		self.template_data["status"] = "OK"
		self.template_data["response"] = api_response["response"]
		self.template_data["title"] = "Status page"
		self.template_data["heading"] = ( "Attaching device to <em>%s</em>" % ( attach_target ) )
		self.template_data["description"] = "Status page show result of operation. In case of success you will see green bar. Otherwise red bar."		
		# Set code and render template
		self.set_response_code( 200 )
		self.render_view()
	#-------------------------------------------------------------------------#
	def detach( self, query ):

		self.template = "status_page.html"

		if not query or "target_pool" not in query or "detach" not in query:
			# We dont have right arguments to complete the action
			self.error_handler( "No arguments was passed." )
			return

		module = "Device"
		# Get function from api
		loaded_module = self.model.load_module( module )
		
		# Prepare parameters
		target_pool = query["target_pool"][0]
		# Device name to detach
		detach = query["detach"][0] 
	
		status, api_response = loaded_module.device_detach( target_pool, detach )
		
		self.template_data["actions"] = [
			{ "name":"Dashboard", "link": "/" },
			{ "name":"Modified pool <em>%s</em>" % target_pool , "link": "/zpool/detail?pool=%s" % target_pool }
		]

		if not status:
			# Something in API went wrong
			self.error_handler( api_response["response"] )
			return

		self.template_data["status"] = "OK"
		self.template_data["response"] = api_response["response"]
		self.template_data["title"] = "Status page"
		self.template_data["heading"] = ( "Detaching device <em>%s</em>" % ( detach ) )
		self.template_data["description"] = "Status page show result of operation. In case of success you will see green bar. Otherwise red bar."		
		# Set code and render template
		self.set_response_code( 200 )
		self.render_view()

	#-------------------------------------------------------------------------#
	def state( self, query ):
	
		self.template = "status_page.html"
		# We dont have arguments or don't have target pool to add device
		if not query or "target_pool" not in query or "target_device" not in query:
			# We dont have right arguments to complete the action
			self.error_handler( "No arguments was passed." )
			return
		# Check for status
		if "status" not in query or query["status"][0] not in [ "online", "offline" ]:
			# In query there is not status or status is invalid.
			self.error_handler( "No status passed or invalid status ( online/offline )" )
			return

		module = "Device"
		# Get function name based of what status we want
		# Get function from api
		loaded_module = self.model.load_module( module )
	
		# Preapare parameters
		target_pool = query["target_pool"][0]
		target_device = query["target_device"][0]

		if query["status"][0] == "online":
			status, api_response = loaded_module.device_online( target_pool, target_device )
		else:
			status, api_response = loaded_module.device_offline( target_pool, target_device )

		self.template_data["actions"] = [
			{ "name":"Dashboard", "link": "/" },
			{ "name":"Modified pool <em>%s</em>" % target_pool , "link": "/zpool/detail?pool=%s" % target_pool }
		]

		if not status:
			# Something in API went wrong
			self.error_handler( api_response["response"] )
			return

		self.template_data["status"] = "OK"
		self.template_data["response"] = api_response["response"]
		self.template_data["title"] = "Status page"
		self.template_data["heading"] = ( "Changing status of <em>%s</em>" % ( target_device ) )
		self.template_data["description"] = "Status page show result of operation. In case of success you will see green bar. Otherwise red bar."		
		# Set code and render template
		self.set_response_code( 200 )
		self.render_view()
	#-------------------------------------------------------------------------#
