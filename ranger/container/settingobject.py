# Copyright (C) 2009, 2010  Roman Zimbelmann <romanz@lavabit.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from inspect import isfunction
from ranger.ext.signals import SignalDispatcher
from ranger.core.shared import FileManagerAware
import re

ALLOWED_SETTINGS = {
	'autosave_bookmarks': (bool, True),
	'collapse_preview': (bool, True),
	'colorscheme_overlay': ((type(None), type(lambda:0)), None),
	'colorscheme': (str, 'default'),
	'column_ratios': ((tuple, list, set), (1, 1, 4, 3)),
	'dirname_in_tabs': (bool, False),
	'display_size_in_main_column': (bool, True),
	'display_size_in_status_bar': (bool, False),
	'draw_bookmark_borders': (bool, True),
	'draw_borders': (bool, False),
	'file_launcher': ((str, bool), 'vim'),
	'flushinput': (bool, True),
	'hidden_filter': (type(re.compile("")),
		re.compile(r"^\.|(pyc|pyo|bak|swp)$|lost\+found")),
	'max_console_history_size': ((int, type(None)), 200),
	'max_history_size': ((int, type(None)), 40),
	'mouse_enabled': (bool, True),
	'padding_right': (bool, True),
	'preview_directories': (bool, True),
	'preview_files': (bool, True),
	'preview_script': ((str, type(None)), None),
	'save_console_history': (bool, True),
	'scroll_offset': (int, 8),
	'shorten_title': (int, 3),
	'show_cursor': (bool, False),
	'show_hidden_bookmarks': (bool, True),
	'show_hidden': (bool, False),
	'sort_case_insensitive': (bool, False),
	'sort_directories_first': (bool, True),
	'sort_reverse': (bool, False),
	'sort': (str, 'basename'),
	'syntax_highlighting': (bool, True),
	'tilde_in_titlebar': (bool, True),
	'update_title': (bool, True),
	'use_preview_script': (bool, True),
	'xterm_alt_key': (bool, False),
}


class SettingObject(SignalDispatcher, FileManagerAware):
	def __init__(self):
		SignalDispatcher.__init__(self)
		self.__dict__['_settings'] = dict()
		for name in ALLOWED_SETTINGS:
			self.signal_bind('setopt.'+name,
					self._raw_set_with_signal, priority=0.2)

	def __setattr__(self, name, value):
		if name[0] == '_':
			self.__dict__[name] = value
		else:
			assert name in ALLOWED_SETTINGS, "No such setting: {0}!".format(name)
			assert self._check_type(name, value)
			kws = dict(setting=name, value=value,
					previous=self._settings.get(name, None), fm=self.fm)
			self.signal_emit('setopt', **kws)
			self.signal_emit('setopt.'+name, **kws)

	def __getattr__(self, name):
		assert name in ALLOWED_SETTINGS or name in self._settings, \
				"No such setting: {0}!".format(name)
		try:
			return self._settings[name]
		except:
			value = ALLOWED_SETTINGS[name][1]
			assert self._check_type(name, value)
			self._raw_set(name, value)
			self.__setattr__(name, value)
			return self._settings[name]

	def __iter__(self):
		for x in self._settings:
			yield x

	def types_of(self, name):
		try:
			typ = ALLOWED_SETTINGS[name][0]
		except KeyError:
			return tuple()
		else:
			if isinstance(typ, tuple):
				return typ
			else:
				return (typ, )


	def _check_type(self, name, value):
		typ = ALLOWED_SETTINGS[name][0]
		if isfunction(typ):
			assert typ(value), \
				"The option `" + name + "' has an incorrect type!"
		else:
			assert isinstance(value, typ), \
				"The option `" + name + "' has an incorrect type!"\
				" Got " + str(type(value)) + ", expected " + str(typ) + "!"
		return True

	__getitem__ = __getattr__
	__setitem__ = __setattr__

	def _raw_set(self, name, value):
		self._settings[name] = value

	def _raw_set_with_signal(self, signal):
		self._settings[signal.setting] = signal.value
