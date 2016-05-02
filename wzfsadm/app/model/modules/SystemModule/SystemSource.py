import subprocess
import json
import re
from app.model.modules.BaseModuleClass import BaseModuleClass
from app.model.ModuleInterface import ModuleInterface

class SystemClass( BaseModuleClass ):
	#-------------------------------------------------------------------------#
	MODULE_NAME = "System Module"
	#-------------------------------------------------------------------------#
	def __init__( self ):
		# Call parent constructor
		BaseModuleClass.__init__( self, self.MODULE_NAME )	
	#-------------------------------------------------------------------------#
	def cpu_stat( self ):

		response = {}
		response["response"] = "Default response"		

		process = subprocess.Popen( [ '/usr/bin/sar', '-u', '1' ],
						stdout=subprocess.PIPE,
						stderr=subprocess.PIPE
					 )

		stdout, stderr = process.communicate()

		if process.returncode != 0:
			response["response"] = stderr
			return ( False, response )	

		lines = stdout.splitlines()
		report = lines.pop()
		statistics = {}
		try:
			time, usr, sys, wio, idle = report.split()
			statistics.update( { "cpu": [ "CPU", 100-int(idle) ] } )
		except ValueError:
			response["response"] = "Invalid sar -u format."
			return False, response
				
		response["data"] = statistics
		return  True, response

	#-------------------------------------------------------------------------#
	def disk_stats( self ):
		
		response = {}
		response["response"] = "Default response"		

		process = subprocess.Popen( [ '/usr/bin/sar', '-d', '1' ],
						stdout=subprocess.PIPE,
						stderr=subprocess.PIPE
					 )

		stdout, stderr = process.communicate()

		if process.returncode != 0:
			response["response"] = stderr
			return ( False, response )	
		lines = stdout.splitlines()
		# Pop unuseful lines
		lines.pop(0)
		lines.pop(0)
		lines.pop(0)
		lines.pop(0)
		lines.pop(0)
		
		# Do for first specific line
		first_line = lines.pop(0)
		tokens = first_line.split()
		if len( tokens ) != 8:
			response["response"] = "Invalid output format"
			return ( False, response )	
		statistics = {}
		devices = []
		device = [ tokens[1], tokens[2] ]
		devices.append( device )
		

		expr = re.compile( '^(sd|cmdk)[1-9]+[0-9]*$' )
		for line in lines:
			# Empty line
			if not line: continue
			tokens = line.split()			
			if len( tokens ) != 7:
				response["response"] = "Invalid output format"
				return ( False, response )	
			if not expr.match( tokens[0] ): continue
			device = [ tokens[0], tokens[1] ]
			devices.append( device )	

		statistics.update( { "disks": devices } )

		response["data"] = statistics
		return  True, response
	#-------------------------------------------------------------------------#
	def system_info( self ):

		response = {}
		response["response"] = "Default response"		

		process = subprocess.Popen( [ '/usr/bin/uname', '-a' ],
						stdout=subprocess.PIPE,
						stderr=subprocess.PIPE
					 )

		stdout, stderr = process.communicate()

		if process.returncode != 0:
			response["response"] = stderr
			return ( False, response )			

		sys_info = {}
		try:
			system, name, release, version, platform, processor, hw = stdout.split()
			sys_info.update( { "OS": system } )
			sys_info.update( { "Name": name } )
			sys_info.update( { "Release": release } )
			sys_info.update( { "Version": version } )
			sys_info.update( { "Platform": platform } )
			sys_info.update( { "Processor": processor } )
			

		except:	
			response["response"] = "Invalid output format of uname command."
			return False, response		
				
		response["data"] = sys_info
		return  True, response

	#-------------------------------------------------------------------------#
