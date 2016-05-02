from app.view.BaseView import BaseView
from app.model.ModuleInterface import ModuleInterface


class BaseController:
	#-------------------------------------------------------------------------#	
	def __init__( self, application ):
	
		self.model = ModuleInterface()	
		self.application = application
		# Set default response
		self.response_code = 200
		self.response = ( "Default", "text/html" )
		# Set templates
		self.template_data = dict()
		self.template = ""				

	#-------------------------------------------------------------------------#
	def render_view( self, mime = "text/html" ):
		# Create view and render view
		view = BaseView()
		response = view.render_template( self.template, self.template_data )		
		self.response = ( response, mime )

	#-------------------------------------------------------------------------#
	def finish( self ):

		self.application.set_code( self.response_code )
		self.application.set_response( self.response )
	#-------------------------------------------------------------------------#
	# Error handling 
	#-------------------------------------------------------------------------#
	def error_handler( self, message ):

		self.template_data["status"] = "ERROR"
		self.template_data["response"] = message
		# We are handling error => redirect to status page
		# Valid request, but something goes wrong
		self.response_code = 200
		self.template = "status_page.html"

		self.render_view() 

	#-------------------------------------------------------------------------#
	# Setters
	#-------------------------------------------------------------------------#
	def set_response( self, response ):
		self.response = response
	#-------------------------------------------------------------------------#
	def set_response_code( self, code ):
		self.response_code = code
	#-------------------------------------------------------------------------#
