#!/usr/bin/env python2.7

import haxor3
import re
from pprint import pprint
from mako.template import Template
from mako.runtime import Context as TemplateContext

class CPPBot(haxor3.Haxor3Bot):
	def __init__(self):
		super(CPPBot, self).__init__()
		self.channels.append("#shadowacre")
		self.lang = self.lang.CPP
		# `haxor3 << "hey"` OR `haxor3 << f(4); int f(int i) {return i*4;}`
		self.lineRgx.append({"name": "cout",    "pattern": re.compile('\s?(<<[^\;]+)\;?(.*)?$')})
		# `{ cout << "hey"; }` OR `{ cout << f(4); } int f(int i) {return i*4;}`
		self.lineRgx.append({"name": "braced",  "pattern": re.compile('(\{.+?\})\s+?(.+)?\;?')}),
		# ANYTHING ELSE
		self.lineRgx.append({"name": "default", "pattern": re.compile('(.*)\;?\s*?$')})

		self.tplIncludes   = ["<iostream>","<functional>"]
		self.tplNamespaces = ["std"]
		self.tplMain       = ""
		self.tplBeforeMain = ""
		self.template = """% for include in includes:
#include ${include}
% endfor
% for ns in namespaces:
using namespace ${ns};
% endfor
${beforeMain}
int main() {${inMain}; return 0;}"""

	def matchedLine(self, rgx, matched):
		print "Matched RGX: " + rgx
		if rgx == "cout":
			self.tplMain = rgx + matched.groups(1)[0]
			self.tplBeforeMain = matched.groups(1)[1]
		elif rgx == "braced":
			self.tplMain = matched.groups(1)[0]
			self.tplBeforeMain = matched.groups(1)[1]
		elif rgx == "default":
			self.tplMain = matched.groups(1)[0]

		ctx = TemplateContext(self.source, includes=self.tplIncludes,
		                      namespaces=self.tplNamespaces,
						      beforeMain=self.tplBeforeMain,
						      inMain=self.tplMain)
		self.renderSource(self.template, ctx)

	def result(self, status):
		if status._run == "AC":
			if status.d_run["stderr"]:
				self.reply(status.d_run["stderr"])
				self.reply("on HE -- " + status.d_run["web_link"])
			elif status.d_run["output"]:
				self.multiMsg(True, status.d_run["output"])
				self.reply("T: " + status.d_run["time_used"] + " --- " + status.d_run["web_link"])
			else:
				self.reply("No output")
		else:
			reason = self._hax.checkStatus(status)
			self.reply("ERROR: Please see below.")
			self.multiMsg(True, reason)

if __name__ == "__main__":
	haxBot = CPPBot()
	haxBot.connect("irc.someplace.com", 6667, "Fib45")
	haxBot.start()
