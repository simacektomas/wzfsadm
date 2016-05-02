import subprocess

class Dataset:
	#-------------------------------------------------------------------------#
	def __init__( self, name ):
		self.dataset_name = name
		self.properties = {}
		self.properties["children"] = [] 	# Array of children datasets
		self.properties["snapshots"] = []
		self.properties["userspace"] = []
		self.properties["groupspace"] = []
		self.properties["name"] = name
		if not self.get_raw_properties():
			raise ValueError 		# Cannot get data

		if not self.parse_properties():
			raise ValueError		# Error during parsing

		if not self.get_raw_children():
			raise ValueError		# Cannot get data about children

		if not self.parse_children():
			raise ValueError		# Error during parsing children

		self.get_snapshots()
		self.get_user_quotas()
		self.get_group_quotas()
		# Object dataset should be initialized
	
	#-------------------------------------------------------------------------#
	def get_raw_properties( self ):
		process = subprocess.Popen( [ '/usr/sbin/zfs', 'get', '-o', 'name,property,value', 'all', self.dataset_name ],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			 )
		
		stdout, stderr = process.communicate()
		if process.returncode != 0:
			# Non zero return code
			return False

		self.raw_properties = stdout
		return True		
	#-------------------------------------------------------------------------#
	def parse_properties( self ):
		
		lines = self.raw_properties.splitlines()
		if not lines[0].split() == [ "NAME", "PROPERTY", "VALUE" ]:
			# Invalid label line 
			return False
		# Get rid of label line
		lines.pop(0)
		for line in lines:
			try:
				tokens = line.split()
				if len( tokens ) > 3:					
					# Creation
					name = tokens[0]
					tokens.pop(0)
					attribute = tokens[0]
					tokens.pop(0)					
					value = " ".join( tokens )					
				elif len( tokens ) == 3:
					# Normal lines
					name = tokens[0]
					attribute = tokens[1]
					value = tokens[2]
				else:
					return False

				if name != self.dataset_name:
					# Input is not for this name
					return False
				# Add attribute to this instance
				self.properties[attribute] = value
				
			except Exception as err:
				print err
				# Invalid line format
				return False
		return True

	#-------------------------------------------------------------------------#
	def get_raw_children( self ):

		process = subprocess.Popen( [ '/usr/sbin/zfs', 'list', '-r' , self.dataset_name ],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			 )

		stdout, stderr = process.communicate()

		if process.returncode != 0:
			# Non zero return code
			return False

		self.raw_children = stdout

		return True
	#-------------------------------------------------------------------------#
	def parse_children( self ):

		lines = self.raw_children.splitlines()
		if not lines[0].split() == [ "NAME", "USED", "AVAIL", "REFER", "MOUNTPOINT" ]:
			# Invalid label line 			
			return False
		lines.pop(0) 					# Get rid of label line
		for line in lines:
			try:
				name, used, avail, refer, mountpoint = line.split()
				if name == self.dataset_name:
					continue		# We already know
				# Add attribute to this instance
				children = {}
				# Fill children data
				children['name'] = name
				children['used'] = used
				children['available'] = avail
				children['referenced'] = refer
				children['mountpoint'] = mountpoint
				self.properties["children"].append( children )
			except Exception as err:
				print err
				# Invalid line formatarguments = [ 'zfs', 'userspace', '-o', 'name,used,quota', self.dataset_name  ]	
				return False
		return True
	#-------------------------------------------------------------------------#
	def get_snapshots( self ):
		

		arguments = [ '/usr/sbin/zfs', 'list', '-r' ,'-t', 'snapshot', '-o', 'name,used,creation', self.dataset_name  ]

		process = subprocess.Popen( arguments ,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			 )

		stdout, stderr = process.communicate()

		if process.returncode != 0:
			# Non zero return code
			return False

		lines = stdout.splitlines()		
		if not lines[0].split() == [ "NAME", "USED", "CREATION" ]:
			return False
		# Get rid of label line
		lines.pop(0)
		for line in lines:
			try:
				snapshot = {}
				tokens = line.split()
				snapshot["name"] = tokens[0]
				# Check if snapshot is of this dataset
				dataset, snapsthot = tokens[0].split( '@' )
				if dataset != self.dataset_name:
					# No more snapshots for this dataset
					return False

				snapshot["used"] = tokens[1]
				tokens.pop(0)
				tokens.pop(0)
				snapshot["creation"] = ' '.join( tokens )
				self.properties["snapshots"].append( snapshot )
			except Exception as err:
				print err
				# Invalid line format
				return False

		return True
	#-------------------------------------------------------------------------#
	def get_user_quotas( self ):

		arguments = [ '/usr/sbin/zfs', 'userspace', '-o', 'name,used,quota', self.dataset_name  ]

		process = subprocess.Popen( arguments ,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			 )

		stdout, stderr = process.communicate()

		if process.returncode != 0:
			# Non zero return code
			return False

                lines = stdout.splitlines()		
		if not lines[0].split() == [ "NAME", "USED", "QUOTA" ]:
			return False
		# Get rid of label line
		lines.pop(0)

		for line in lines:
			try:
				user = {}
				tokens = line.split()
				user["name"] = tokens[0]				
				user["used"] = tokens[1]				
				user["quota"] = tokens[2]
				self.properties["userspace"].append( user )
			except Exception as err:
				print err
				# Invalid line format
				return False

		return True
		

	#-------------------------------------------------------------------------#	
	def get_group_quotas( self ):

		arguments = [ '/usr/sbin/zfs', 'groupspace', '-o', 'name,used,quota', self.dataset_name  ]

		process = subprocess.Popen( arguments ,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			 )

		stdout, stderr = process.communicate()

		if process.returncode != 0:
			# Non zero return code
			return False

                lines = stdout.splitlines()		
		if not lines[0].split() == [ "NAME", "USED", "QUOTA" ]:
			return False
		# Get rid of label line
		lines.pop(0)

		for line in lines:
			try:
				group = {}
				tokens = line.split()
				group["name"] = tokens[0]				
				group["used"] = tokens[1]				
				group["quota"] = tokens[2]
				self.properties["groupspace"].append( group )
			except Exception as err:
				print err
				# Invalid line format
				return False

		return True
	#-------------------------------------------------------------------------#
	def get_children( self ):
		return self.children
	#-------------------------------------------------------------------------#
	def get_properties( self ): 
		return self.properties
	#-------------------------------------------------------------------------#

