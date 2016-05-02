from app.model.modules.BaseModuleClass import BaseModuleClass
import subprocess

class DeviceClass( BaseModuleClass ):
	#-------------------------------------------------------------------------#
	MODULE_NAME = "Dataset Module"
	#-------------------------------------------------------------------------#
	def __init__( self ):
		# Call parent constructor
		BaseModuleClass.__init__( self, self.MODULE_NAME )	
	#-------------------------------------------------------------------------#
	def add_device( self, target_pool, devices, device_type = None, forced = False ):

		response = {}
		response["response"] = "Default response"
		# Target pool is empty

		if self.SAFE_MODE and self.expr.match( target_pool ):
			response["response"] = "Application is running in safe mode. Cannot process operation over system pool rpool."
			return ( False, response )

		if not target_pool:
			response["response"] = "Empty target pool. Cannot add device."
			return ( False, response )
		# Zpool add arguments
		if not devices:
			response["response"] = "Empty devices. Cannot add device to pool with empty devices."
			return ( False, response )

		arguments = devices		
		# Validate device_type
		if device_type in [ "mirror", "raidz", "raidz1", "raidz2", "raidz3", "cache", "log", "none" ]:
			# Device type is not none
			if device_type != "none":
				arguments.insert( 0, device_type )
		else:
			# Not valid device type
			response["response"] = "Not valid device type."
			return ( False, response )
		# Add target pool
		arguments.insert( 0, target_pool )
		# If command should be forced
		if forced:
			arguments.insert( 0, "-f" )
		# Basic command structure
		arguments.insert( 0, "add" )
		arguments.insert( 0, "/usr/sbin/zpool" )

		process = subprocess.Popen( arguments,
					    stdout=subprocess.PIPE,
					    stderr=subprocess.PIPE
					  )

		stdout, stderr = process.communicate()

		if process.returncode != 0:
			# Some error during adding device to zpool
			response["response"] = stderr
			return ( False, response )

		response["response"] = ( "You have succesfuly added vdevice %s to zpool %s. Command %s was succesful" % 
											( device_type, target_pool, " ".join( arguments )) ) 
		return ( True, response )
	#-------------------------------------------------------------------------#
	def device_online( self, target_pool, target_device ):

		response = {}
		response["response"] = "Default response"

		if self.SAFE_MODE and self.expr.match( target_pool ):
			response["response"] = "Application is running in safe mode. Cannot process operation over system pool rpool."
			return ( False, response )

		process = subprocess.Popen( [ "/usr/sbin/zpool", "online", target_pool, target_device ],
					    stdout=subprocess.PIPE,
					    stderr=subprocess.PIPE
					  )

		stdout, stderr = process.communicate()

		if process.returncode != 0:
			# Some error during adding device to zpool
			response["response"] = stderr
			return ( False, response )

		response["response"] = ( "You have succesfully changed %s device status to online" % ( target_device ) )

		return ( True, response )
	#-------------------------------------------------------------------------#
	def device_offline( self, target_pool, target_device ):
		response = {}
		response["response"] = "Default response"

		if self.SAFE_MODE and self.expr.match( target_pool ):
			response["response"] = "Application is running in safe mode. Cannot process operation over system pool rpool."
			return ( False, response )

		process = subprocess.Popen( [ "/usr/sbin/zpool", "offline", target_pool, target_device ],
					    stdout=subprocess.PIPE,
					    stderr=subprocess.PIPE
					  )

		stdout, stderr = process.communicate()

		if process.returncode != 0:
			# Some error during adding device to zpool
			response["response"] = stderr
			return ( False, response )

		response["response"] = ( "You have succesfully changed %s device status to offline" % ( target_device ) )

		return ( True, response )
	#-------------------------------------------------------------------------#
	def device_attach( self, target_pool, attach_target, device ):
		response = {}
		response["response"] = "Default response"

		if self.SAFE_MODE and self.expr.match( target_pool ):
			response["response"] = "Application is running in safe mode. Cannot process operation over system pool rpool."
			return ( False, response )

		if not target_pool or not attach_target or not device:
			response["response"] = "Empty argument, cannot proccess command."
			return ( False, response )

		process = subprocess.Popen( [ "/usr/sbin/zpool", "attach", target_pool, attach_target, device ],
					    stdout=subprocess.PIPE,
					    stderr=subprocess.PIPE
					  )

		stdout, stderr = process.communicate()

		if process.returncode != 0:
			# Some error during adding device to zpool
			response["response"] = stderr
			return ( False, response )

		response["response"] = ( "You have succesfully attached %s device to %s device in %s" % ( device, attach_target, target_pool ) )

		return ( True, response )
	#-------------------------------------------------------------------------#
	def device_detach( self, target_pool, detach_target ):
		response = {}
		response["response"] = "Default response"

		if self.SAFE_MODE and self.expr.match( target_pool ):
			response["response"] = "Application is running in safe mode. Cannot process operation over system pool rpool."
			return ( False, response )

		# Check for argumetns
		if not target_pool or not detach_target:
			response["response"] = "Empty argument, cannot proccess command."
			return ( False, response )
		# Detach device from zpool
		process = subprocess.Popen( [ "/usr/sbin/zpool", "detach", target_pool, detach_target ],
					    stdout=subprocess.PIPE,
					    stderr=subprocess.PIPE
					  )

		stdout, stderr = process.communicate()

		if process.returncode != 0:
			# Some error during adding device to zpool
			response["response"] = stderr
			return ( False, response )

		response["response"] = ( "You have succesfully dectached %s device from zpool %s" % ( detach_target, target_pool ) )

		return ( True, response )
	#-------------------------------------------------------------------------#
