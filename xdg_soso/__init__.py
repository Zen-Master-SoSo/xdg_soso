#  xdg_soso/xdg_soso/__init__.py
#
#  Copyright 2026 Leon Dionne <ldionne@dridesign.sh.cn>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
This module provides the "XDGSetup" class for installing your package as
a userspace application on xdg compliant shells.
"""
import logging
from os import unlink, getenv, getlogin
from shutil import copy2
from pathlib import Path
import xml.etree.ElementTree as et
from xml.etree.ElementTree import Element
from tempfile import gettempdir
from subprocess import run

__version__ = "1.3.1"

SVG = 'svg'
PNG = 'png'


def is_xdg():
	"""
	Checks that this is running on an XDG -compliant system
	"""
	for var in ['XDG_CONFIG_DIRS', 'XDG_DATA_DIRS']:
		if getenv(var):
			return True
	return run(['which', 'update-desktop-database'], check = False).returncode == 0

def _check(attrib, value, type_, list_elem_type = None):
	if not isinstance(value, type_):
		raise ValueError(f'Incorrect type for "{attrib}": "{type(value).__name__}"')
	if type_ is list and value:
		for elem in value:
			if not isinstance(elem, list_elem_type):
				raise ValueError(f'Incorrect type for "{attrib}": "{type(elem).__name__}"')

def _icon_suffix(fmt):
	return '.svg' if fmt == SVG else '.png'


class XDGMime:
	"""
	Encapsulates a mime type, associating it with a glob pattern
	"""

	def __init__(self, name, glob_pattern = None, *, comment = None, subclass_of = None):
		self._name = name
		self._glob_pattern = glob_pattern
		self._comment = comment
		self._subclass_of = subclass_of

	def __str__(self):
		return self._name

	def __repr__(self):
		return f'<XDGMime "{self._name}">'

	def append_xml_elem(self, root_node, module_name = None):
		elem = et.SubElement(root_node, 'mime-type')
		elem.attrib['type'] = self._name
		if self._comment:
			el = et.SubElement(elem, 'comment')
			el.text = self._comment
		if self._glob_pattern:
			el = et.SubElement(elem, 'glob')
			el.attrib['pattern'] = self._glob_pattern
		if self._subclass_of:
			el = et.SubElement(elem, 'sub-class-of')
			el.attrib['type'] = self._subclass_of
		if module_name:
			el = et.SubElement(elem, 'generic-icon')
			el.attrib['name'] = module_name


class XDGSetup:
	"""
	Installs your package as a userspace application on XDG compliant shells.
	"""

	def __init__(self, module_name, name = None):
		"""
		"root_path" is for testing: files will be saved in root_path/share/... instead
		of $HOME/.local/share/...
		"""
		self.module_name = module_name
		self.name = name or module_name
		self._root_path = Path.home() / '.local' / 'share'
		self._modify_system = True
		# Properties:
		self.__comment = None
		self.__vendor_name = None
		self.__keywords = None
		self.__categories = None
		self.__mime_types = []
		self.__custom_mime_type = None
		self.__application_icons = {}
		self.__generic_icon = None
		self.__file_icons = {}
		# Temp file:
		self.__mime_xml_temp = None

	# ----------------------
	# Properties set by user

	@property
	def comment(self):
		"""
		What will be displayed in desktop applications like Dash or your file explorer.
		"""
		return self.__comment

	@comment.setter
	def comment(self, value):
		_check('comment', value, str)
		self.__comment = value

	@property
	def vendor_name(self):
		"""
		A word or phrase, preferably your organizations name. The purpose of the vendor
		prefix is to prevent name conflicts.
		"""
		return self.__vendor_name

	@vendor_name.setter
	def vendor_name(self, value):
		_check('vendor_name', value, str)
		self.__vendor_name = value

	@property
	def keywords(self):
		"""
		Makes it possible for the user to search for your application using Dash or other tools.
		"""
		return self.__keywords

	@keywords.setter
	def keywords(self, value):
		_check('keywords', value, list, str)
		self.__keywords = value

	@property
	def categories(self):
		"""
		Used by some tools to create a hierarchical menu.
		"""
		return self.__categories

	@categories.setter
	def categories(self, value):
		_check('categories', value, list, str)
		self.__categories = value

	@property
	def application_icon(self):
		"""
		Paths to custom icons which will be displayed in the task bar / switcher.

		You can set this property twice, once with a .png icon, and once with an .svg icon.

		Alternatively, name both icons the same except for the extension and put them
		in the same directory, and set this property to the name of either one without
		the extension. This class will discover both.

		Returns dict { SVG: Path, PNG: Path }
		"""
		return self.__application_icons

	@application_icon.setter
	def application_icon(self, value):
		_check('application_icon', value, (str, Path))
		self.__application_icons.update(self._src_icon_dict(value))

	@property
	def generic_icon(self):
		"""
		The NAME of a generic icon which you want to be displayed in the task bar / switcher.
		"""
		return self.__generic_icon

	@generic_icon.setter
	def generic_icon(self, value):
		_check('generic_icon', value, (str, Path))
		self.__generic_icon = value

	@property
	def mime_types(self):
		"""
		A list of XDGMime objects which your application may handle. XDG will associate
		your application with all of the given mime_types.
		"""
		return self.__mime_types

	@mime_types.setter
	def mime_types(self, value):
		_check('mime_types', value, list, XDGMime)
		self.__mime_types = value

	@property
	def custom_mime_type(self):
		"""
		An XDGMime object defining a mimetype that the system will open with your
		program BY DEFAULT.
		"""
		return self.__custom_mime_type

	@custom_mime_type.setter
	def custom_mime_type(self, value):
		_check('custom_mime_type', value, XDGMime)
		self.__custom_mime_type = value

	@property
	def file_icon(self):
		"""
		The icon which will be used by the file manager to decorate files which should
		be associated with your application.

		You can set this property twice, once with a .png icon, and once with an .svg icon.

		Alternatively, name both icons the same except for the extension and put them
		in the same directory, and set this property to the name of either one without
		the extension. This class will discover both.

		Returns dict { SVG: Path, PNG: Path }
		"""
		return self.__file_icons

	@file_icon.setter
	def file_icon(self, value):
		_check('file_icon', value, (str, Path))
		self.__file_icons.update(self._src_icon_dict(value))

	# --------------------------------
	# More property setting functions:

	def append_mime_type(self, mime_type):
		"""
		Append an XDGMime object to the list of mime_types that your application will handle.
		"""
		_check('mime_type', mime_type, XDGMime)
		self.mime_types.append(mime_type)

	# --------------------------------------
	# Icon file discovery and disambiguation

	def _src_icon_dict(self, value):
		path = Path(value)
		icons = {}
		svg_icon = path.parent / (path.stem + '.svg')
		png_icon = path.parent / (path.stem + '.png')
		if svg_icon.exists():
			icons[SVG] = svg_icon
		if png_icon.exists():
			icons[PNG] = png_icon
		return icons

	# -------------------------------------------
	# Paths returned from standard user locations

	@property
	def desktop_file(self):
		"""
		The target path to the .desktop file which descibes your application to the
		operating system.
		"""
		return self._check_path(self._root_path / 'applications' / (
			self.module_name + '.desktop'))

	def _application_icon_file(self, fmt):
		"""
		The target path of the application icon for the given format.
		"fmt" may be one of the constants SVG or PNG.
		"""
		return self._check_path(self._user_icon_path(fmt) / 'apps' /
			(self.module_name + _icon_suffix(fmt)))

	def _file_icon_file(self, fmt):
		"""
		The target path of the file icon (icons used to decorate files which are
		associated with your application in the file manager) for the given format.
		"fmt" may be one of the constants SVG or PNG.
		"""
		return self._check_path(self._user_icon_path(fmt) / 'mimetypes' / (
			str(self.__custom_mime_type).replace('/', '-') + _icon_suffix(fmt)))

	@property
	def mime_xml_file(self):
		"""
		The target path of the mime_type definition file for your application.
		"""
		return self._check_path(self._root_path / 'mime' / 'packages' / (
			self._xml_mime_name() + '.xml'))

	def _xml_mime_name(self):
		module_name = self.module_name.replace('/', '-')
		return f'{self.__vendor_name}-{module_name}' if self.__vendor_name else module_name

	def _user_icon_path(self, fmt):
		return self._root_path / 'icons' / 'hicolor' / ('scalable' if fmt == SVG else '48x48')

	def _check_path(self, path):
		if not path.parent.exists():
			path.parent.mkdir(parents = True)
		return path

	# -----------------------
	# Installation functions:

	def installed(self):
		"""
		Returns True if the appropriate .desktop file for your application exists.
		"""
		return self.desktop_file.exists()

	def install(self, root_path = None):
		"""
		Installs .desktop file and other optional components, like application_icon and
		mime_type associations.

		Setting "root_path" to a directory name will make the installer save target
		files beneath the given directory name. This is used for debugging. If
		"root_path" is given, no actual XDG commands will be issued.
		"""
		if root_path:
			self._root_path = Path(root_path)
			self._modify_system = False
		for fmt, icon_path in self.__application_icons.items():
			if icon_path.exists():
				target = self._application_icon_file(fmt)
				copy2(icon_path, target)
				logging.debug('Copied application icon to "%s"', target)
		self._make_desktop_file()
		if self.__mime_types or self.__custom_mime_type:
			self._make_mime_xml_file()
			self._xdg_mime_install()
			if self.__custom_mime_type:
				self._set_mime_default()
		for fmt, icon_path in self.__file_icons.items():
			if icon_path.exists():
				target = self._file_icon_file(fmt)
				copy2(icon_path, target)
				logging.debug('Copied file icon to "%s"', target)
		if self.__application_icons or self.__file_icons:
			self._update_icon_caches()
		self._update_desktop_database()
		print(f'Successfully installed {self.name} for {getlogin()} on this machine.')

	def _make_desktop_file(self):
		with open(str(self.desktop_file), 'w', encoding = 'utf-8') as fob:
			fob.write(f"""[Desktop Entry]
Version=1.0
Name={self.name}
Exec=/usr/bin/python3 -m {self.module_name}
Terminal=false
Type=Application
""")
			if self.comment:
				fob.write(f'Comment={self.__comment}\n')
			if self.__application_icons:
				fob.write(f'Icon={self.module_name}\n')
			if self.__generic_icon:
				fob.write(f'Icon={self.__generic_icon}\n')
			if self.__keywords:
				string = ';'.join(self.__keywords) + ';'
				fob.write(f'Keywords={string}\n')
			if self.__categories:
				string = ';'.join(self.__categories) + ';'
				fob.write(f'Categories={string}\n')
			if self.__mime_types or self.__custom_mime_type:
				string = ';'.join(str(mime_type) for mime_type in self.__mime_types)
				if self.__custom_mime_type:
					string = f'{self.__custom_mime_type};' + string
				fob.write(f'MimeType={string};\n')
		logging.debug('Created desktop file "%s"', self.desktop_file)
		self.desktop_file.chmod(0o755)

	def _make_mime_xml_file(self):
		"""
		Make a mime_type xml file.
		"""
		et.register_namespace('', 'http://www.freedesktop.org/standards/shared-mime-info')
		tree = et.ElementTree(et.fromstring(
			'<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info"/>'))
		root = tree.getroot()
		if self.__custom_mime_type:
			self.__custom_mime_type.append_xml_elem(root, self.module_name)
		for mime_type in self.__mime_types:
			mime_type.append_xml_elem(root)
		self.__mime_xml_temp = Path(gettempdir()) / (self._xml_mime_name() + '.xml')
		with open(self.__mime_xml_temp, 'wb') as fob:
			tree.write(fob, xml_declaration = True, encoding = 'utf-8')
		logging.debug('Write mime xml file "%s"', self.__mime_xml_temp)
		if not self._modify_system:
			copy2(self.__mime_xml_temp, self.mime_xml_file)

	# ------------
	# XDG commands

	def _xdg_mime_install(self):
		if self.__vendor_name:
			self._run([ 'xdg-mime', 'install', self.__mime_xml_temp ])
		else:
			self._run([ 'xdg-mime', 'install', '--novendor', self.__mime_xml_temp ])
		logging.debug('Mimetype file should be found at "%s"', self.mime_xml_file)
		unlink(self.__mime_xml_temp)

	def _set_mime_default(self):
		self._run([ 'xdg-mime', 'default', self.desktop_file.name, str(self.__custom_mime_type) ])

	def _update_desktop_database(self):
		self._run([ 'update-desktop-database', self._shared_dir('applications') ])

	def _update_mime_database(self):
		self._run([ 'update-mime-database', self._shared_dir('mime') ])

	def _update_icon_caches(self):
		for path in [
			Path('icons') / 'hicolor' / 'scalable' / 'apps',
			Path('icons') / 'hicolor' / 'scalable' / 'mimetypes'
		]:
			self._run([ 'update-icon-caches', self._shared_dir(path) ])

	def uninstall(self):
		try:
			self._run([ 'xdg-mime', 'uninstall', self.mime_xml_file])
		except RuntimeError as err:
			logging.error(err)
		for fmt in self.__application_icons:
			self._application_icon_file(fmt).unlink()
		for fmt in self.__file_icons:
			self._file_icon_file(fmt).unlink()
		self.desktop_file.unlink()
		self._update_mime_database()
		self._update_icon_caches()
		print(f'Successfully uninstalled {self.name} for {getlogin()} on this machine.')

	# ----------------
	# Helper functions

	def _shared_dir(self, subpath):
		return (self._root_path or Path.home()) / subpath

	def _run(self, *args):
		logging.debug(args)
		if self._modify_system:
			cp = run(*args, check = False, capture_output = True)
			if cp.returncode != 0:
				raise RuntimeError(cp.stderr)


#  end xdg_soso/xdg_soso/__init__.py
