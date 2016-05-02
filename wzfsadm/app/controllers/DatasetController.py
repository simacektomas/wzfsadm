import re
from BaseController import BaseController

class DatasetController( BaseController ):
	#-------------------------------------------------------------------------#
	def detail( self, query ):
		
		self.template = "dataset_detail.html"

		if not query or "dataset" not in query:
			# We dont have right arguments to complete the action
			self.error_handler( "No arguments was passed." )
			return	

		module = "Dataset"
		# Get function from api
		loaded_module = self.model.load_module( module )
		dataset = query["dataset"][0]

		status, api_response = loaded_module.get_dataset( dataset )

		if not status:
		# Something in API goes wrong
			self.error_handler( api_response["response"] )
			return
		# Get data from datasetinstance
		dataset_instance = api_response["data"]
		dataset_properties = dataset_instance.get_properties()
		# Fill template
		self.template_data["dataset"] = dataset_properties
		self.template_data["title"] = "Detail dataset"
		self.template_data["heading"] = ( "Dataset <em>%s</em>" % ( dataset ) )
		self.template_data["description"] = "Dataset detail page offers information about specific dataset. You can manage it\'s properties from this page. You can create child datasets, take snapshots, change properties or setting up quotas."
		# Get all dataset in datasets
		sets = dataset.split('/')
		tmp = []
		navigation = []
		navigation.append( { "name": sets[0]+" pool", "link": "/zpool/detail?pool=%s" % sets[0] } )

		for parent in sets:
			tmp.append( parent )
			navigation.append( { "name": parent, "link": "/dataset/detail?dataset=%s" % "/".join( tmp ) } )
		
		active = navigation.pop()
		self.template_data["bread"] = navigation
		self.template_data["active"] = active

		self.set_response_code( 200 )
		self.render_view()	

	#-------------------------------------------------------------------------#
	def create( self, query ):
		
		self.template = "status_page.html"

		if not query or "dataset" not in query:
			# We dont have right arguments to complete the action
			self.error_handler( "No arguments was passed." )
			return
		
		module = "Dataset"
		# Get function from api
		loaded_module = self.model.load_module( module )			
		# Get dataset name from query
		dataset = query["dataset"][0]		
		create_parents = False
		# Check if user wants to create all parents
		if "parents" in query:
			create_parents = True

		self.template_data["actions"] = [
			{ "name":"Dashboard", "link": "/" }			
		]

		status, api_response = loaded_module.create_dataset( dataset, create_parents )
		if not status:
		# Something in API goes wrong
			self.error_handler( api_response["response"] )
			return

		self.template_data["response"] = api_response["response"]
		self.template_data["status"] = "OK"	
		self.template_data["title"] = "Status page"
		self.template_data["heading"] = ( "Creating dataset <em>%s</em>" % ( dataset ) )
		self.template_data["description"] = "Status page show result of operation. In case of success you will see green bar. Otherwise red bar."
		self.template_data["actions"].append( { "name":"Created dataset <em>%s</em>" % dataset , "link": "/dataset/detail?dataset=%s" % dataset } )		

		self.set_response_code( 200 )
		self.render_view()
	#-------------------------------------------------------------------------#
	def destroy( self, query ):
		
		self.template = "status_page.html"

		if not query or "dataset" not in query:
			# We dont have right arguments to complete the action
			self.error_handler( "No arguments was passed." )
			return	

		module = "Dataset"
		# Get function from api
		loaded_module = self.model.load_module( module )		
		dataset = query["dataset"][0]
		forced = False
		destroy_children = False
		# Command should be forced
		if "forced" in query:
			forced = True
		# Should destroy all children
		if "children" in query:
			destroy_children = True
		# Calling destroy_dataset
		status, api_response = loaded_module.destroy_dataset( dataset, destroy_children, forced )
		if not status:
		# Something in API goes wrong
			self.error_handler( api_response["response"] )
			return

		self.template_data["response"] = api_response["response"]
		self.template_data["status"] = "OK"	
		self.template_data["title"] = "Status page"
		self.template_data["heading"] = ( "Destroying dataset <em>%s</em>" % ( dataset ) )
		self.template_data["description"] = "Status page show result of operation. In case of success you will see green bar. Otherwise red bar."
		self.template_data["actions"] = [
			{ "name":"Dashboard", "link": "/" }
		]
		self.set_response_code( 200 )
		self.render_view()

	#-------------------------------------------------------------------------#
	def snapshot( self, query ):

		self.template = "status_page.html"
		

		if not query or "snapshot" not in query or "dataset" not in query:
			# We dont have right arguments to complete the action
			self.error_handler( "No arguments was passed." )
			return	

		module = "Dataset"
		# Get function from api
		loaded_module = self.model.load_module( module )
		dataset = query["dataset"][0]
		snapshot = query["snapshot"][0]
		descendant = False

		self.template_data["actions"] = [
			{ "name":"Dashboard", "link": "/" },
			{ "name":"Dataset <em>%s</em>" % dataset , "link": "/dataset/detail?dataset=%s" % dataset }
		]
		# Shoud snapshot be created for all descendant datasets
		if "descendant" in query:
			descendant = True	

		status, api_response = loaded_module.create_snapshot( dataset, snapshot, descendant )

		if not status:
		# Something in API goes wrong
			self.error_handler( api_response["response"] )
			return

		self.template_data["response"] = api_response["response"]
		self.template_data["status"] = "OK"
		self.template_data["title"] = "Status page"
		self.template_data["heading"] = ( "Creating snapshot <em>%s</em>" % ( dataset+'@'+snapshot ) )
		self.template_data["description"] = "Status page show result of operation. In case of success you will see green bar. Otherwise red bar."	
		self.template_data["actions"].append( { "name":"Snapshot %s" % dataset+"@"+snapshot, "link":"/dataset/detail?dataset=%s" % dataset+"@"+snapshot } )		

		self.set_response_code( 200 )
		self.render_view()
	#-------------------------------------------------------------------------#
	def mount( self, query ):

		self.template = "status_page.html"

		if not query or "dataset" not in query:
			# We dont have right arguments to complete the action
			self.error_handler( "No arguments was passed." )
			return


		module = "Dataset"
		# Get function from api
		loaded_module = self.model.load_module( module )
		dataset = query["dataset"][0]
		mount_options = []
		# Check for temporary mount options
		if "readonly" in query:
			mount_options.append( query["readonly"][0] )
		if "exec" in query:
			mount_options.append( query["exec"][0] )
		if "setuid" in query:
			mount_options.append( query["setuid"][0] )
		# Mountpoint is set and not empty
		if "mountpoint" in query and query["mountpoint"][0]:
			mount_options.append( "mountpoint=%s" % ( query["mountpoint"][0] ) )

		status, api_response = loaded_module.mount_dataset( dataset, mount_options )

		self.template_data["actions"] = [
			{ "name":"Dashboard", "link": "/" },
			{ "name":"Dataset <em>%s</em>" % dataset , "link": "/dataset/detail?dataset=%s" % dataset }
		]

		if not status:
		# Something in API goes wrong
			self.error_handler( api_response["response"] )
			return

		self.template_data["response"] = api_response["response"]
		self.template_data["status"] = "OK"
		self.template_data["title"] = "Status page"
		self.template_data["heading"] = ( "Mounting dataset <em>%s</em>" % ( dataset ) )
		self.template_data["description"] = "Status page show result of operation. In case of success you will see green bar. Otherwise red bar."
			

		self.set_response_code( 200 )
		self.render_view()
	#-------------------------------------------------------------------------#
	def unmount( self, query ):

		self.template = "status_page.html"

		if not query or "dataset" not in query:
			# We dont have right arguments to complete the action
			self.error_handler( "No arguments was passed." )
			return	
				
		module = "Dataset"
		function_name = "unmount_dataset"
		# Get function from api
		loaded_module = self.model.load_module( module )		
		dataset = query["dataset"][0]
		forced = False
		# Check if command should be forced executed
		if "forced" in query:
			forced = True

		self.template_data["actions"] = [
			{ "name":"Dashboard", "link": "/" },
			{ "name":"Dataset <em>%s</em>" % dataset , "link": "/dataset/detail?dataset=%s" % dataset }
		]

		status, api_response = loaded_module.unmount_dataset( dataset, forced )		

		if not status:
		# Something in API goes wrong
			self.error_handler( api_response["response"] )
			return

		self.template_data["response"] = api_response["response"]
		self.template_data["status"] = "OK"
		self.template_data["title"] = "Status page"
		self.template_data["heading"] = ( "Unmounting dataset <em>%s</em>" % ( dataset ) )
		self.template_data["description"] = "Status page show result of operation. In case of success you will see green bar. Otherwise red bar."

		self.set_response_code( 200 )
		self.render_view()
	#-------------------------------------------------------------------------#
	def rollback( self, query ):
	
		self.template = "status_page.html"

		if not query or "snapshot" not in query:
			# We dont have right arguments to complete the action
			self.error_handler( "No arguments was passed." )
			return	
	
		module = "Dataset"
		# Get function from api
		loaded_module = self.model.load_module( module )	
		snapshot = query["snapshot"][0]
		destroy_more_recent = False
		# Check if command should be forced executed
		if "recent" in query:
			destroy_more_recent = True

		status, api_response = loaded_module.rollback_dataset( snapshot, destroy_more_recent )		

		self.template_data["actions"] = [
			{ "name":"Dashboard", "link": "/" },
			{ "name":"Snapshot <em>%s</em>" % snapshot , "link": "/dataset/detail?dataset=%s" % snapshot }
		]

		if not status:
		# Something in API goes wrong
			self.error_handler( api_response["response"] )
			return

		self.template_data["response"] = api_response["response"]
		self.template_data["status"] = "OK"
		self.template_data["title"] = "Status page"
		self.template_data["heading"] = ( "Rolling back to snapshot <em>%s</em>" % ( snapshot ) )
		self.template_data["description"] = "Status page show result of operation. In case of success you will see green bar. Otherwise red bar."	
		self.template_data["actions"].append( { "name":"Rollbacked dataset %s" % snapshot.split('@')[0], "link":"/dataset/detail?dataset=%s" % snapshot.split('@')[0] } )			

		self.set_response_code( 200 )
		self.render_view()
	#-------------------------------------------------------------------------#
	def setproperty( self, query ):

		self.template = "status_page.html"
		if not query or "dataset" not in query or "property" not in query or "value" not in query:
			# We dont have right arguments to complete the action
			self.error_handler( "No arguments was passed." )
			return		

		module = "Dataset"
		# Get function from api
		loaded_module = self.model.load_module( module )		
		# Gather parameters from URL
		dataset = query["dataset"][0]
		property_name = query["property"][0]
		property_value = query["value"][0]
		recursively = False
		# Check if command should be forced executed
		if "recursively" in query:
			recursively = True
		
		self.template_data["actions"] = [
			{ "name":"Dashboard", "link": "/" },
			{ "name":"Modified dataset <em>%s</em>" % dataset , "link": "/dataset/detail?dataset=%s" % dataset }
		]

		status, api_response = loaded_module.property_set( dataset, property_name, property_value, recursively )		

		if not status:
		# Something in API goes wrong
			self.error_handler( api_response["response"] )
			return

		self.template_data["response"] = api_response["response"]
		self.template_data["status"] = "OK"
		self.template_data["title"] = "Status page"
		self.template_data["heading"] = ( "Setting property to dataset <em>%s</em>" % ( dataset ) )
		self.template_data["description"] = "Status page show result of operation. In case of success you will see green bar. Otherwise red bar."

		self.set_response_code( 200 )
		self.render_view()
	#-------------------------------------------------------------------------#
	def quota( self, query ):

		self.template = "status_page.html"
		if not query or "type" not in query or query["type"][0] not in [ 'user', 'group' ]:
			# We dont have right arguments to complete the action
			self.error_handler( "No arguments was passed. Or bad type arguments" )
			return

		if "dataset" not in query or "name" not in query or "quota" not in query:
			# We dont have right arguments to complete the action
			self.error_handler( "No arguments was passed. Or bad arguments" )
			return

		dataset = query["dataset"][0]
		quota_type = query["type"][0]			

		module = "Dataset"		
		# Get function from api
		loaded_module = self.model.load_module( module )

		name = query["name"][0]
		quota = query["quota"][0]
		recursively = False
		if "recursively" in query:
			recursively = True
		
		if quota_type == "user":
			status, api_response = loaded_module.user_quota( dataset, name, quota, recursively )	
		else:
			status, api_response = loaded_module.group_quota( dataset, name, quota, recursively )	
			
		self.template_data["actions"] = [
			{ "name":"Dashboard", "link": "/" },
			{ "name":"Modified dataset <em>%s</em>" % dataset , "link": "/dataset/detail?dataset=%s" % dataset }
		]

		if not status:
		# Something in API goes wrong
			self.error_handler( api_response["response"] )
			return

		self.template_data["response"] = api_response["response"]
		self.template_data["status"] = "OK"
		self.template_data["title"] = "Status page"
		self.template_data["heading"] = ( "Setting quota to dataset <em>%s</em>" % ( dataset ) )
		self.template_data["description"] = "Status page show result of operation. In case of success you will see green bar. Otherwise red bar."

		self.set_response_code( 200 )
		self.render_view()	
	#-------------------------------------------------------------------------#
