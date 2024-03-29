import sys, os, re
import sublime
import sublime_plugin
import subprocess
try:
	from cStringIO import *
except:
	from StringIO import *
try:
	import xml.sax
except:
	pass

SETTINGS = 'xml-guesser.sublime-settings'
DEFAULTS = { }

class Options:
	'''cleaner settings syntax with defaults'''
	def __init__(self, settings, defaults):
		self._name = settings
		self._defaults = defaults
		self._settings = sublime.load_settings(settings)
	def flush(self):
		for k, v in self._defaults.iteritems():
			if not self._settings.has(k):
				self._settings.set(k, v)
		sublime.save_settings(self._name)
	def __getattr__(self, name):
		if name in self._defaults:
			return self._settings.get(name, self._defaults[name])
		return self._settings.get(name)
	def __setattr__(self, name, value):
		if name in ('_name','_defaults','_settings'):
			self.__dict__[name] = value
			return
		self._settings.set(name, value)
		sublime.save_settings(self._name)

opts = Options(SETTINGS, DEFAULTS)
opts.flush()

class XmlGuessListener(sublime_plugin.EventListener):
	'''Look in the first few lines of the file for something resembling XML'''
	def plain_syntax(self, view):
		for s in opts.syntaxes_to_check:
			if s in view.settings().get("syntax"): return True
		return False

	def get_text(self, view):
		return view.substr(sublime.Region(0, view.size()))

	def get_lines(self, view, maxlines = None):
		text = sublime.Region(0, view.size())
		lines = view.split_by_newlines(text)
		if maxlines is not None:
			lines = lines[0:min(maxlines, len(lines))]
		return [view.substr(reg) for reg in lines]

	def xml_declaration(self, view):
		'''easiest way, pattern matching on the head of the file'''
		if not opts.check_xml_declaration: return False
		lines = self.get_lines(view, opts.check_xml_declaration_lines)
		line = '\n'.join(lines).rstrip()
		return re.search(r'^<\?xml\s+version=[^>]+\?>', line, re.S | re.M | re.I) is not None

	def magic(self, view):
		'''open a pipe to /usr/bin/file and see what it says'''
		if not opts.check_magic: return False
		if not os.path.exists(opts.check_magic_command): return False
		
		cmd = [ opts.check_magic_command, '-' ]
		print '$',cmd
		p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
		out, _ = p.communicate(self.get_text(view))
		out = out.lower().strip()
		print out
		if opts.check_magic_sgml_ok and 'sgml' in out:
			return True
		return 'xml' in out

	def try_parse(self, view):
		'''attempt parsing it with sax'''
		if not opts.check_parser: return False
		# xml.sax wasn't imported
		if not 'xml.sax' in sys.modules: return False
		try:
			print 'parsing view contents'
			parser = xml.sax.make_parser()
			parser.setContentHandler(xml.sax.handler.ContentHandler())
			stream = StringIO(self.get_text(view))
			parser.parse(stream)
			return True
		except Exception, e:
			print e
			return False

	def run_command(self, view):
		'''set the syntax once we're done'''
		sublime.set_timeout(lambda: view.set_syntax_file(opts.syntax_file), 1)

	def on_load(self, view):
		# first things first, if there's already a mode set, move on
		if not self.plain_syntax(view):
			return
		if self.xml_declaration(view) \
				or self.try_parse(view) \
				or self.magic(view):
			self.run_command(view)
