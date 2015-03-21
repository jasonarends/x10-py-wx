#!/usr/bin/python

# python wrapper for heyu that tries to keep track of known state in a sqlite3 database
# of course this doesn't account for manual changes, but eh

import sys
import sqlite3 as lite
import os, datetime

if len(sys.argv)>1:

	# sys.argv.pop()
	# pop the first argument, it's the script name

	con = lite.connect('/home/pi/database.db')

	with con:

		cur = con.cursor()


		for arg in sys.argv:

			if len(arg.split(','))<2:
				continue
			else:


				device = arg.split(',')[0]

				if 'on' in arg.split(',')[1]:
					active = '1'
					heyucmd = 'fon'
				elif 'off' in arg.split(',')[1]:
					active = '0'
					heyucmd = 'foff'
				else:
					continue


				cur.execute("update x10 set active = '%(act)s', timestamp = ? where device = '%(dev)s'" % {"act" : active, "dev" : device},[datetime.datetime.now()])
				os.system('heyu ' + heyucmd + ' ' + device)

