# Volatility Malcom plugin
#
# Copyright (C) 2015 Digitalis (https://www.facebook.com/digitalisx) 
#
# Thanks to MaJ3stY (saiwnsgud@naver.com)
#
# Thanks to n0fate (http://forensic.n0fate.com, volafox)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details. 
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA 

import os
import sys
import shutil
import requests
import json
import volatility.utils as utils
import volatility.plugins.procdump as procdump

malcom_key = "--- Your Malwares.com API Key ---"

class malcom(procdump.ProcDump):
	"""Process Dump & Malwares.com Scan Plugin."""

	def __init__(self, config, *args, **kwargs):
		procdump.ProcDump.__init__(self, config, *args, **kwargs)
		config.add_option('OFFSET', short_option = 'o', default = None, help = 'EPROCESS offset (in hex) in the physical address space', action = 'store', type = 'int')
		config.add_option('PID', short_option = 'p', default = None, help = 'Operate on these Process IDs (comma-separated)', action = 'store', type = 'str')

	def calculate(self):
		
		if self._config.DUMP_DIR == None:
			print "\n[!] Process to dump in the current directory."
			self._config.DUMP_DIR = os.getcwd()
		
		if self._config.PID != None:
			print "\n[+] To start a process dump.\n"
			result = procdump.ProcDump(self._config).execute()
			result2 = procdump.ProcDump.calculate(self)	
			filepath = self._config.DUMP_DIR + "\executable.{0}.exe".format(self._config.PID)
			filename = "executable.{0}.exe".format(self._config.PID)
			copypath = self._config.DUMP_DIR + "\Volatility\plugins" + "\executable.{0}.exe".format(self._config.PID)

			shutil.copy(filepath, copypath)

			print "\n[+] Copying Dump File ..."
			print "[-] Copy Dump File Path : " + copypath

			return filename
		
	def render_text(self, outfd, data):

		print "[+] Upload File & File Analysis ..."

		params = {'api_key':malcom_key,'filename': data}
		files = {'file':(data,open(data,'rb'), 'application/octet-stream')}
		response = requests.post('https://www.malwares.com/api/v2/file/upload', files=files, data=params)
		json_response = response.json() # File_Upload
		
		md5 = json_response["md5"]

		params = {'api_key':malcom_key, 'hash':md5}
		response = requests.get('https://www.malwares.com/api/v2/file/mwsinfo', params=params)
		json_response = response.json() # File_Scan

		result_msg = json_response["result_msg"]
		date = json_response["date"]
		md5 = json_response["md5"]
		sha1 = json_response["sha1"]
		sha256 = json_response["sha256"]
		view_count = json_response["view_count"]
		black_white = json_response["black_white"]
		filetype = json_response["filetype"]
		filesize = json_response["filesize"]
		first_seen = json_response["first_seen"]
		avscan = json_response["virustotal"]
		positives = avscan["positives"]
		total = avscan["total"]

		print "\n[!] Upload Information"
		print "[-] Upload Result : " + result_msg
		print "[-] Upload Date : " + date
	
		print "\n[!] File Information"
		print "[-] MD5 : " + md5
		print "[-] SHA1 : " + sha1
		print "[-] SHA256 : " + sha256
		
		print "\n[!] File Advanced Information"
		print "[-] View Count : " + str(view_count)
		print "[-] First Seen : " + first_seen
	
		if(black_white == 1):
			print "[-] Black & White List : Black List" 

		else:
			print "[-] Black & White List : White List"

		print "[-] File Type : " + filetype
		print "[-] File Size : " + str(filesize) + " Byte"
		print "\n[!] AV Scan Result : " + str(positives) + " / " + str(total)