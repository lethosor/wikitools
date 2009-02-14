﻿# -*- coding: utf-8 -*-
# Copyright 2008, 2009 Mr.Z-man,  bjweeks

# This file is part of wikitools.
# wikitools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
 
# wikitools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
 
# You should have received a copy of the GNU General Public License
# along with wikitools.  If not, see <http://www.gnu.org/licenses/>.

import wiki, page, api, socket

class User:
	""" A user on the wiki
	wiki - A wiki object
	name - The username, as a string
	check - Checks for existence, normalizes name
	"""	
	def __init__(self, site, name, check=True):
		self.site = site
		self.name = name
		if not isinstance(self.name, unicode):
			self.name = unicode(self.name, 'utf8')
		self.exists = True # If we're not going to check, assume it does
		self.blocked = False
		self.editcount = -1
		self.groups = []
		if check:
			self.setUserInfo()
		self.isIP = False
		try:
			s = socket.inet_aton(self.name.replace(' ', '_'))
			if socket.inet_ntoa(s) == self.name:
				self.isIP = True
				self.exists = False
		except:
			pass
		self.page = page.Page(self.site, ':'.join([self.site.namespaces[2]['*'], self.name]), check=check, followRedir=False)
	
	def setUserInfo(self):
		"""
		Sets basic user info
		"""		
		params = {
			'action': 'query',
			'list': 'users',
			'ususers':self.name,
			'usprop':'blockinfo|groups|editcount'
		}
		req = api.APIRequest(self.site, params)
		response = req.query()
		user = response['query']['users'][0]
		self.name = user['name']
		if 'missing' in user or 'invalid' in user:
			self.exists = False
			return
		self.editcount = int(user['editcount'])
		if 'groups' in user:
			self.groups = user['groups']
		if 'blockedby' in user:
			self.blocked = True
			
	def block(self, reason=False, expiry=False, anononly=False, nocreate=False, autoblock=False, noemail=False, hidename=False, allowusertalk=False, reblock=False):
		params = {'action':'block',
			'user':self.name,
			'gettoken':''
		}
		req = api.APIRequest(self.site, params)
		res = req.query()
		token = res['block']['blocktoken']
		params = {'action':'block',
			'user':self.name,
			'token':token
		}
		if reason:
			params['reason'] = reason
		if expiry:
			params['expiry'] = expiry
		if anononly:
			params['anononly'] = ''
		if nocreate:
			params['nocreate'] = ''
		if autoblock:
			params['autoblock'] = ''
		if noemail:
			params['noemail'] = ''
		if hidename:
			params['hidename'] = ''
		if allowusertalk:
			params['allowusertalk'] = ''
		if reblock:
			params['reblock'] = ''
		req = api.APIRequest(self.site, params, write=False)
		res = req.query()
		if 'block' in res:
			self.blocked = True
		return res
		
	def unblock(self, reason=False):
		params = {
		    'action': 'unblock',
			'user': self.name,
			'gettoken': ''
		}
		req = api.APIRequest(self.site, params)
		res = req.query()
		token = res['unblock']['unblocktoken']
		params = {
		    'action': 'unblock',
			'user': self.name,
			'token': token
		}
		if reason:
			params['reason'] = reason
		req = api.APIRequest(self.site, params, write=False)
		res = req.query()
		if 'unblock' in res:
			self.blocked = False
		return res
	
	def __eq__(self, other):
		if not isinstance(other, User):
			return False
		if self.name == other.name and self.site == other.wiki:
			return True
		return False
	def __ne__(self, other):
		if not isinstance(other, User):
			return True
		if self.name == other.name and self.site == other.wiki:
			return False
		return True
			
		