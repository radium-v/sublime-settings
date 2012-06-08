import sublime
import sublime_plugin
import re
import time
import base64
import htmlentitydefs
from cgi import escape
from hashlib import md5
from datetime import datetime
from dateutil.parser import parse

class ConvertTabsToSpacesCommand(sublime_plugin.TextCommand):
    """Convert Tabs To Spaces"""
    def run(self, edit):
        sublime.status_message('Convert tabs to spaces.')
        tab_size = int(self.view.settings().get('tab_size', 4))

        for region in self.view.sel():
            if not region.empty():
                self.view.replace(edit, region, self.view.substr(region).expandtabs(tab_size))
        else:
            self.view.run_command('select_all')
            self.view.replace(edit, self.view.sel()[0], self.view.substr(self.view.sel()[0]).expandtabs(tab_size))
            self.view.sel().clear()


class ConvertSpacesToTabsCommand(sublime_plugin.TextCommand):
    """Convert Spaces To Tabs"""
    def run(self, edit):
        sublime.status_message('Convert spaces to tabs.')
        tab_size = str(self.view.settings().get('tab_size', 4))

        for region in self.view.sel():
            if not region.empty():
                self.view.replace(edit, region, re.sub(r' {' + tab_size + r'}', r'\t', self.view.substr(region)))
        else:
            self.view.run_command('select_all')
            self.view.replace(edit, self.view.sel()[0], re.sub(r' {' + tab_size + r'}', r'\t', self.view.substr(self.view.sel()[0])))
            self.view.sel().clear()


class ConvertCharsToHtmlCommand(sublime_plugin.TextCommand):
    """Convert Chars into XML/HTML Entities"""
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                self.view.replace(edit, region, escape(self.view.substr(region), True))


class ConvertHtmlToCharsCommand(sublime_plugin.TextCommand):
    """Convert XML/HTML Entities into Chars"""
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = re.sub('&(%s);' % '|'.join(htmlentitydefs.name2codepoint),
                    lambda m: unichr(htmlentitydefs.name2codepoint[m.group(1)]), self.view.substr(region))
                self.view.replace(edit, region, text)


class ConvertCamelUnderscoresCommand(sublime_plugin.TextCommand):
    """Convert CamelCase to under_scores and vice versa"""
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                text = self.toCamelCase(text) if '_' in text else self.toUnderscores(text)
                self.view.replace(edit, region, text)

    def toUnderscores(self, name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def toCamelCase(self, name):
        return ''.join(map(lambda x: x.capitalize(), name.split('_')))


class ConvertToUnicodeNotationCommand(sublime_plugin.TextCommand):
    """Convert string to Unicode notation"""
    def run(self, edit):
        pattern = re.compile(r'\s+')

        for region in self.view.sel():
            if not region.empty():
                text = ''
                for c in self.view.substr(region):
                    if not re.match(pattern, c) and (c < 0x20 or c > 0x7e):
                        text += '\\u{0:04X}'.format(ord(c))
                    else:
                        text += c

                self.view.replace(edit, region, text)


class ConvertFromUnicodeNotationCommand(sublime_plugin.TextCommand):
    """Convert string from Unicode notation"""
    def run(self, edit):
        pattern = re.compile(r'(\\u)([0-9a-fA-F]{2,4})')

        for region in self.view.sel():
            if not region.empty():
                text = re.sub(pattern, lambda m: unichr(int(m.group(2), 16)), self.view.substr(region))
                self.view.replace(edit, region, text)


class ConvertToBase64Command(sublime_plugin.TextCommand):
    """Encode string with base64"""
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region).encode(self.enc())
                self.view.replace(edit, region, base64.b64encode(text))

    def enc(self):
        if self.view.encoding() == 'Undefined':
            return self.view.settings().get('default_encoding', 'UTF-8')
        else:
            return self.view.encoding()


class ConvertFromBase64Command(sublime_plugin.TextCommand):
    """Decode string with base64"""
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                try:
                    text = base64.b64decode(self.view.substr(region).encode(self.enc()))
                    self.view.replace(edit, region, text.decode('utf-8'))
                except:
                    sublime.status_message('Convert error.')

    def enc(self):
        if self.view.encoding() == 'Undefined':
            return self.view.settings().get('default_encoding', 'UTF-8')
        else:
            return self.view.encoding()


class ConvertMd5Command(sublime_plugin.TextCommand):
    """Calculate MD5 hash"""
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region).encode(self.enc())
                self.view.replace(edit, region, md5(text).hexdigest())

    def enc(self):
        if self.view.encoding() == 'Undefined':
            return self.view.settings().get('default_encoding', 'UTF-8')
        else:
            return self.view.encoding()


class ConvertTimeFormatCommand(sublime_plugin.TextCommand):
    """This will allow you to convert epoch to human readable date and vice versa"""
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                result = self.from_unix(text) if re.match(ur'^([0-9]+)$', text) else self.to_unix(text)

                if result:
                    self.view.replace(edit, region, result)
                else:
                    sublime.status_message('Convert error.')

    def from_unix(self, timestamp):
        sublime.status_message('Convert from epoch to human readable date.')
        return datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M")

    def to_unix(self, timestr):
        sublime.status_message('Convert from human readable date to epoch.')
        try:
            return '%d' % (time.mktime(parse(timestr).timetuple()))
        except:
            return False


class InsertTimestampCommand(sublime_plugin.TextCommand):
    """This will allow you to insert timestamp to current position"""
    def run(self, edit):
        for region in self.view.sel():
            self.view.insert(edit, region.begin(), datetime.now().strftime("%Y-%m-%d %H:%M"))
