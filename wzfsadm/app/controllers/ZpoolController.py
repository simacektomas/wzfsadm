from BaseController import BaseController
import json

class ZpoolController( BaseController ):
	#-------------------------------------------------------------------------#
	# Render formular for creating zpool
	def createform( self, query ):
		# Set template that we want to render
		self.template = "zpool_create_form.html"		
		
		module = "Pool"
		# Get function from api
		loaded_module = self.model.load_module( module )	

		# We have function => call it list_sources()
		status, api_response = loaded_module.list_sources()

		if not status:
		# Something in API goes wrong
			self.error_handler( api_response["response"] )
			return
		# Fill template data
		# Redirect after filling form
		self.template_data["action"] = "/zpool/create"
		self.template_data["sources"] = api_response["data"]	
		self.template_data["title"] = "Create pool"
		self.template_data["heading"] = "Form for creating poool"
		self.template_data["description"] = "You can create pool on this page. Just choose from available sources, pick type of virtual device and fill name."			

		self.set_response_code( 200 )
		self.render_view()

	#-------------------------------------------------------------------------#
	def create( self, query ):

		self.template = "status_page.html"

		if not query or "name" not in query:
			# We dont have right arguments to complete the action
			self.error_handler( "No arguments was passed." )
			return			
	
		# We have query
		# We want to create zpool
		module = "Pool"
		function_name = "create_zpool"
		loaded_module = self.model.load_module( module )		
		# Prepare arguments 					
		# Prepare parameters for zpool api			
		pool_type = None
		ro = False
		forced = False
		# Get name from query array
		name = query["name"][0]
		devices = []

		if "device" in query:
			devices = query["device"]

		if "type" in query:
			pool_type = query["type"][0]
		if "forced" in query:
			forced = True
		# Call the function from api create_zpool( name, resources )
		status, api_response = loaded_module.create_zpool( name, devices, pool_type, forced )
		self.template_data["actions"] = [
			{ "name":"Dashboard", "link": "/" }
		
		]
		if not status:
			# Something in API goes wrong
			self.error_handler( api_response["response"] )
			return

		self.template_data["response"] = api_response["response"]
		self.template_data["status"] = "OK"
		self.template_data["title"] = "Status page create pool"
		self.template_data["heading"] = ( "Creationg pool <em>%s</em>" % ( name ) )
		self.template_data["description"] = "Status page show result of operation. In case of success you will see green bar. Otherwise red bar."				
		self.template_data["actions"].append( { "name":"Created pool <em>%s</em>" % name , "link": "/zpool/detail?pool=%s" % name } )
		# Set response
		self.set_response_code( 200 )
		# Render template 
		self.render_view()

	#-------------------------------------------------------------------------#
	# Destroy zpool
	def destroy( self, query ):

		self.template = "status_page.html"

		if not query or "pool" not in query:
			# We dont have right arguments to complete the action
			self.error_handler( "No arguments was passed." )
			return

		module = "Pool"
		# Get function from api
		loaded_module = self.model.load_module( module )
		# Get name from query string to destroy zpool
		pool = query["pool"][0]
		status, api_response = loaded_module.destroy_zpool( pool )

		self.template_data["actions"] = [
			{ "name":"Dashboard", "link": "/" }
		]

		if not status:
		# Something in API goes wrong
			self.error_handler( api_response["response"] )
			return
	    
		self.template_data["response"] = api_response["response"]
		self.template_data["status"] = "OK"
		self.template_data["title"] = "Status page destroy pool"
		self.template_data["heading"] = ( "Destroying pool <em>%s</em>" % ( pool ) )
		self.template_data["description"] = "Status page show result of operation. In case of success you will see green bar. Otherwise red bar."		
		self.set_response_code( 200 )
		self.render_view()

	#-------------------------------------------------------------------------#
	def detail( self, query ):

		self.template = "pool_detail.html"

		if not query or "pool" not in query:
			# We dont have right arguments to complete the action
			self.error_handler( "No arguments was passed." )
			return
		
		module = "Pool"
		# Get function from api
		loaded_module = self.model.load_module( module )
		# Get pool name from query
		pool = query["pool"][0]
		status, api_response = loaded_module.get_zpool( pool )

		status3, api_response3 = loaded_module.history( pool )

		if not status:
			# Something in API goes wrong
			self.error_handler( api_response["response"] )
			return

		if not status3:
			# Something in API goes wrong
			self.error_handler( api_response3["response"] )
			return

		module = "Dataset"
		loaded_module = self.model.load_module( module )

		status2, api_response2 = loaded_module.get_dataset( pool )

		if not status2:
			# Something in API goes wrong
			self.template_data["dataset"] = []
		else:
			self.template_data["dataset"] = api_response2["data"].get_properties()		
		
		# Api call was correct
		# Set template data 
		self.template_data["zpool"] = api_response["data"]
		self.template_data["history"] = api_response3["data"]
		self.template_data["title"] = "Detail"
		self.template_data["heading"] = ( "Pool <em>%s</em>" % ( pool ) )
		self.template_data["description"] = "Pool detail page offers information about specific pool. You can manage it\'s properties from this page like add another device or set some properites."

		self.set_response_code( 200 )
		self.render_view()		
	#-------------------------------------------------------------------------#
	def setproperty( self, query ):

		self.template = "status_page.html"

		if not query or "target_pool" not in query or "value" not in query or "property" not in query:
			# We dont have right arguments to complete the action
			self.error_handler( "No arguments was passed." )
			return

		module = "Pool"
		# Get function from api
		loaded_module = self.model.load_module( module )

		target_pool = query["target_pool"][0]
		property_name = query["property"][0]
		property_value = query["value"][0]
		status, api_response = loaded_module.property_set( target_pool, property_name, property_value )

		self.template_data["actions"] = [
			{ "name":"Dashboard", "link": "/" },
			{ "name":"Modified pool <em>%s</em>" % target_pool , "link": "/zpool/detail?pool=%s" % target_pool }
		]

		if not status:
			# Something in API goes wrong
			self.error_handler( api_response["response"] )
			return

		self.template_data["response"] = api_response["response"]
		self.template_data["status"] = "OK"
		self.template_data["title"] = "Status page"
		self.template_data["heading"] = ( "Setting property of pool <em>%s</em>" % ( target_pool ) )
		self.template_data["description"] = "Status page show result of operation. In case of success you will see green bar. Otherwise red bar."		
		self.set_response_code( 200 )
		self.render_view()	

	#-------------------------------------------------------------------------#
