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
This module provides the "XDGSetup" class for installing your python script as
a userspace application on xdg compliant shells.
"""
import logging
from os import linesep, unlink, getenv
from shutil import copy2
from pathlib import Path
import xml.etree.ElementTree as et
from xml.etree.ElementTree import Element
from tempfile import mkstemp
from subprocess import run, CalledProcessError

__version__ = "0.1.1"


def _run(*args):
	logging.debug(args)
	run(*args, check = True)


class XDGSetup:
	"""
	Installs your package as a userspace application on XDG compliant shells.
	"""

	comment = None
	keywords = None
	categories = None
	application_icon = None
	mime_type = None
	glob_pattern = None
	file_icon = None

	quiet = False
	root_path = None		# For testing - fakeout XDG paths

	def __init__(self, module_name, name = None):
		self.module_name = module_name
		self.name = name or module_name

	@property
	def desktop_file(self):
		return self._file(
			Path('applications'),
			self.module_name + '.desktop')

	@property
	def app_icon_file(self):
		return self._file(
			Path('icons') / 'hicolor' / 'scalable' / 'apps',
			self.module_name + Path(self.application_icon).suffix)

	@property
	def file_icon_file(self):
		return self._file(
			Path('icons') / 'hicolor' / 'scalable' / 'mimetypes',
			self.mime_type.replace('/', '-') + Path(self.file_icon).suffix)

	@property
	def mime_xml_file(self):
		return self._file(
			Path('mime') / 'packages',
			self.module_name + '.xml')

	@classmethod
	def is_xdg(cls):
		"""
		Checks that this is running on an XDG -compliant system
		"""
		for var in ['XDG_CONFIG_DIRS', 'XDG_DATA_DIRS']:
			if getenv(var):
				return True
		return False

	def install(self):
		if self.application_icon:
			copy2(self.application_icon, self.app_icon_file)
		if self.application_icon or self.file_icon:
			self.update_icon_caches()
		self.make_desktop_file()
		if self.mime_type:
			self.make_mime_type()
			if self.file_icon:
				copy2(self.file_icon, self.file_icon_file)
				self.update_icon_caches()
			if self.glob_pattern:
				self.set_mime_default()
		self.update_desktop_database()

	def make_desktop_file(self):
		content = f"""[Desktop Entry]
Version=1.0
Name={self.name}
Exec=/usr/bin/python3 -m {self.module_name}
Terminal=false
Type=Application
"""
		if self.comment:
			content += f'Comment={self.comment}{linesep}'
		if self.application_icon:
			content += f'Icon={self.module_name}{linesep}'
		if self.keywords:
			keywords = ';'.join(self.keywords) + ';'
			content += f'Keywords={keywords}{linesep}'
		if self.categories:
			categories = ';'.join(self.categories) + ';'
			content += f'Categories={categories}{linesep}'
		if self.mime_type:
			content += f'MimeType={self.mime_type}{linesep}'
		self.desktop_file.write_text(content, encoding = 'utf-8')

	def make_mime_type(self):
		"""
		Make a mime_type xml file.
		"""
		et.register_namespace('', 'http://www.freedesktop.org/standards/shared-mime-info')
		tree = et.ElementTree(et.fromstring(
			'<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info"/>'))
		root = tree.getroot()
		mimetype = et.SubElement(root, 'mime-type')
		mimetype.attrib['type'] = self.mime_type
		if self.comment:
			el = et.SubElement(mimetype, 'comment')
			el.text = self.comment
		if self.glob_pattern:
			el = et.SubElement(mimetype, 'glob')
			el.attrib['pattern'] = self.glob_pattern
		if self.application_icon:
			el = et.SubElement(mimetype, 'generic-icon')
			el.attrib['name'] = self.module_name
		fh, filename = mkstemp(prefix = 'mimetype-', suffix = '.xml')
		try:
			tree.write(fh, xml_declaration = True, encoding = 'utf-8')
		except Exception as e:
			raise e
		else:
			if self.root_path:
				copy2(filename, self.mime_xml_file)
			else:
				_run([ 'xdg-mime', 'install', filename ])
		finally:
			unlink(filename)

	def set_mime_default(self):
		_run([ 'xdg-mime', 'default', self.desktop_file.name, self.mime_type ])

	def update_desktop_database(self):
		_run([ 'update-desktop-database', self._shared_dir('applications') ])

	def update_mime_database(self):
		_run([ 'update-mime-database', self._shared_dir('mime') ])

	def update_icon_caches(self):
		_run([ 'update-icon-caches', self._shared_dir('icons') / '*' ])

	def uninstall(self):
		_run([ 'xdg-mime', 'uninstall', self.mime_xml_file])
		unlink(self.mime_xml_file)
		unlink(self.app_icon_file)
		unlink(self.file_icon_file)
		unlink(self.desktop_file)
		self.update_mime_database()
		self.update_icon_caches()

	def _shared_dir(self, subpath):
		return (self.root_path or Path.home()) / '.local' / 'share' / subpath

	def _file(self, subpath, name):
		dirpath = self._shared_dir(subpath)
		try:
			dirpath.mkdir(parents = True)
		except FileExistsError:
			pass
		return dirpath / name


#  end xdg_soso/xdg_soso/__init__.py
