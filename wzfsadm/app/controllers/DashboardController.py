from BaseController import BaseController
import json

class DashboardController( BaseController ):
	#-------------------------------------------------------------------------#
	def index( self, query ):
		# Dont care about query, this is first page
		self.template = "dashboard.html"

		module = "Pool"
		loaded_module = self.model.load_module( module )		

		# Load module
		status, api_response = loaded_module.get_zpool_all()

		status3, api_response3 = loaded_module.history()
		
		if not status:
			# Somethin in API goes wrong
			self.error_handler( api_response["response"] )
			return

		if not status3:
			# Somethin in API goes wrong
			self.error_handler( api_response3["response"] )
			return
		# Done with calling get_zpool_all
		# Now call get_dataset_all
		module = "Dataset"
		loaded_module = self.model.load_module( module )		
		# Call function from API
		status2, api_response2 = loaded_module.get_dataset_all()
		
		if not status2:
			# Somethin in API goes wrong
			self.error_handler( api_response2["response"] )
			return	

		module = "System"
		loaded_module = self.model.load_module( module )		
		# Call function from API
		status4, api_response4 = loaded_module.system_info()
		
		if not status4:
			# Somethin in API goes wrong
			self.error_handler( api_response4["response"] )
			return	
		# We have all data we need				

		# Api call was correct
		# Set template data 
		self.template_data["jumbo"] = True
		self.template_data["zpools"] = api_response["data"]
		self.template_data["datasets"] = api_response2["data"]
		self.template_data["title"] = "Dashboard"
		self.template_data["history"] = api_response3["data"]
		self.template_data["system"] = api_response4["data"]
		self.template_data["heading"] = "Welcome to wzfsadm application"
		self.template_data["description"] = "This application provide basic function to controll ZFS file system. This page is overview of avaliable pools and datasets."

		self.set_response_code( 200 )
		self.render_view()	
	#-------------------------------------------------------------------------#
	def cpu( self, query ):

		self.template = "plain.html"

		module = "System"
		loaded_module = self.model.load_module( module )

		status, api_response = loaded_module.cpu_stat()
		
		if not status:
			# Somethin in API goes wrong
			self.error_handler( api_response["response"] )
			return
		
		self.template_data["stats"] = json.dumps( api_response["data"], indent = 4 )
		self.set_response_code( 200 )
		self.render_view( "text/plain" )
		
	#-------------------------------------------------------------------------#
