import jinja2

class BaseView():
	#-------------------------------------------------------------------------#
	TEMPLATE_PATH = "/usr/wzfsadm/templates/"
	#-------------------------------------------------------------------------#
	def __init__( self ):
		# Load jinja2 template engine template loader and enviroment
		self.template_loader = jinja2.FileSystemLoader( searchpath = self.TEMPLATE_PATH )
		self.template_env = jinja2.Environment( loader = self.template_loader )


	#-------------------------------------------------------------------------#
	def render_template( self, template, template_data ):
			rendered = ""
		# Load template
#		try:		
			loaded_template = self.template_env.get_template( template )
			# Fill template
			rendered = loaded_template.render( template_data )		
#		except Exception as excp :
			
		# Return filled template
			return rendered

	#-------------------------------------------------------------------------#
