#!/usr/bin/env python2.7

import re
from pprint import pprint
from mako.template import Template
from mako.runtime import Context as TemplateContext
from StringIO import StringIO

import irc.client
from hackerearth.parameters import SupportedLanguages
from hackerearth.parameters import RunAPIParameters
from hackerearth.api_handlers import HackerEarthAPI

class Haxor3Status:
	_compile  = None
	d_compile = None
	_run      = None
	d_run     = None

class Haxor3(object):
	def __init__(self):
		self.client_secret = '0a7f0101e5cc06e4417a3addeb76164680ac83a4'
		self.compressed = 1
		self.html = 0

	def submitSource(self, params):
		api_params = RunAPIParameters(
			client_secret=self.client_secret, compressed=self.compressed, html=self.html,
			lang=params["lang"], source=params["source"])

		self.api = HackerEarthAPI(api_params)

	def compileSource(self, status):
		c = self.api.compile()
		status.d_compile = c.__dict__
		status._compile = status.d_compile["compile_status"]
		return status

	def runSource(self, status):
		status = self.compileSource(status)
		if status._compile == "OK":
			r = self.api.run()
			status.d_run = r.__dict__
			if status.d_run.has_key("status"):
				status._run = status.d_run["status"]
			else:
				status._run = "NULL"
		return status

	def checkStatus(self, status):
		pprint(status.d_compile)
		if status._compile == "OK":
			if not status.d_compile.has_key("status"):
				return "No detail. See " + status.d_run["web_link"]
			else:
				return "NULL. Please find my maker :("
		else:
			return status._compile


class Haxor3Bot(irc.client.SimpleIRCClient):
	def __init__(self):
		super(Haxor3Bot, self).__init__()
		self._hax     = Haxor3()
		self.lang     = SupportedLanguages
		self.lineRgx  = []
		self.channels = []
		self.replyTo  = ""
		self.channelFrom = ""

		self.source = StringIO()

	def on_welcome(self, connection, event):
		for channel in self.channels:
			connection.join(channel)

		self.channelFrom = self.channels[0]

	def on_pubmsg(self, connection, event):
		self.channelFrom = event.target
		self.replyTo = event.source.nick
		matchedName = re.match("^"+connection.get_nickname()+"(\:|,|\s)\s?(.*)", event.arguments[0])
		if matchedName:
			if self.enterLine(matchedName.groups(1)):
				self.runCode()

	def on_quit(self, connection, event):
		pprint(event.source)

	def matchedLine(self, rgx, matched): pass
	def results(self, status): pass

	def enterLine(self, input):
		for rgx in self.lineRgx:
			matched = rgx["pattern"].match(input[1])
			if matched:
				self.matchedLine(rgx["name"], matched)
				return True

		self.reply('Input not understood. Please speak to my creator. He may bless your endevours.')
		return False

	def renderSource(self, template, ctx):
		tpl = Template(template)
		tpl.render_context(ctx)
		self._hax.submitSource({"source": self.source.getvalue(), "lang": self.lang})
		self.source.close()
		self.source = StringIO()

	def runCode(self):
		status = Haxor3Status()
		self.result(self._hax.runSource(status))
		pprint(status.d_run)

	def say(self, text):
		if text != None:
			self.connection.privmsg(self.channelFrom, text)

	def reply(self, text):
		if text != None:
			self.connection.privmsg(self.channelFrom, self.replyTo + " " + text)

	def multiMsg(self, sayreply, text):
		lines = text.split("\n")
		for line in lines[:5]:
			if sayreply:
				self.say(line)
			else:
				self.reply(line)
