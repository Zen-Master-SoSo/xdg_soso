# xdg_soso

Installs a python script as an application on XDG compliant shells.

Installation is done for the current user in the user's home directory. Root
access is not needed. THIS DOES NOT INSTALL A PYTHON APPLICATION SYSTEM-WIDE -
just in the user's home directory.

## Installation

```bash
$ pip install xdg_soso
```

## Usage

In your python application:

```python
from xdg_soso import XDGSetup
```

Create an instance of XDGSetup and install your application:

```python
xdg = XDGSetup(__package__, "MyModule")
xdg.comment = __doc__	# For example
[..set other attributes..]
xdg.install()
```

A better way is to constuct a class which inherits from XDGSetup. That way, you
can do an uninstall using the same class as you would use to do an install:

```python
class MyInstaller(XDGSetup):
	def __init__():
		super().__init__(__package__, "MyModule")
		self.comment = __doc__	# For example
		[..set other attributes..]

installer = MyInstaller()
installer.install()
```

And to uninstall:

```python
installer = MyInstaller()
installer.uninstall()
```

## Attributes

You need at a bare minumum the module name. A "friendly name" is nice to have,
but if you don't provide it, the module name will be used. It's probably a good
idea to include an application icon, as well. There are two properties which
you can use to set an application icon: "application_icon" and "generic_icon".
(See below)

The attributes which you can set include:

#### comment

(str)

What will be displayed in desktop applications like Dash or your file explorer.

#### keywords

(list of str)

Makes it possible for the user to search for your application using Dash or other tools.

Some common keywords include:

> ALSA, AccessX, Accessibility, Accounting, Appearance, Audio, Avatar,
Background, Balance, Battery, Bluetooth, Brightness, Broadcast, Button,
Capture, Chart, Color, Configuration, Configure, Contrast, DAW,
DVD, Desktop, Dim, Display, Document, Drivers, E-mail, Editor, Email, Equation,
Fax, Feed, Fingerprint, Headset, Image, Keyboard, Language, Launcher, Layout, Lock, Login,
MIDI, MP2, MP3, MathML, Menus, Microphone, Monitor, Mouse, Mousepad,
Network, Newsgroup, Partition, Password, Picture, Player, Plugin, Power, Preferences,
Printer, Process, Profile, Projector, RSS, Repositories, Resolution,
Screen, Security, Sequencer, Server, Settings, Slideshow, Stylus, Synthesizer, System,
Tablet, Task, Text, Theme, Trackball, Trackpad, Transform, Unity, User, Video,
View, Viewer, Volume, WAV, Wacom, Wallpaper, Wireless, Zoom

#### categories

(list of str)

Used by some tools to create a hierarchical menu.

Some common categories include:

> 2DGraphics, Application, Archiving, Audio, AudioVideo, AudioVideoEditing,
Calculator, Compression, Core, Database, DesktopSettings, Development,
Documentation, Email, FileTools, FileTransfer, Filesystem, GNOME, GTK,
Graphics, HardwareSettings, IDE, Math, Midi, Monitor, Music, Network, Office,
Photography, Player, Printing, Qt, RasterGraphics, Recorder, Screensaver,
Security, Sequencer, Settings, Spreadsheet, System, TV, TerminalEmulator,
TextEditor, Utilities, Utility, VectorGraphics, Video, Viewer, WordProcessor,
XFCE

#### application_icon

(str or Path)

A file path to a custom icon which will be displayed in the task bar /
switcher. For example:

```python
xdg = XDGSetup('my_package', 'My Package Name')
xdg.application_icon = join(dirname(__file__), 'application-icon.svg')
```

#### generic_icon

(str)

The NAME of a generic icon which you want to be displayed in the task bar /
switcher. Some generic icon names include:

> help-about, media-playback-start, document-print, emblem-important,
applications-graphics, x-office-calendar

You can use one of the generic icons like so:

```python
xdg = XDGSetup('my_package', 'My Package Name')
xdg.generic_icon = 'x-office-calendar'
```

#### mime_types

(list of str)

A list of XDGMime objects which define which mime_types to associate with your program.

#### file_icon

(str or Path)

The icon which will be used by the file manager to decorate files which should
be associated with your application using the "mime_type" declared for your
application's files.

In order to use this feature, you must decide on a mime_type name and set the
"mime_type" attribute on the installer to what you have decided. (See
"mime_type" and "glob_pattern" above)

### Complete example:

```python
from pathlib import Path
from xdg_soso import XDGSetup

class FooInstaller(XDGSetup):
	def __init__():
		super().__init__(__package__, 'Name To Call It')
		self.comment = "A concise description of my project."
		self.mime_type = 'x-application/foo'
		self.glob_pattern = '*.foo'
		self.application_icon = Path(__file__).parent / 'res' / 'application-icon.svg'
		self.file_icon = Path(__file__).parent / 'res' / 'file-icon.svg'
		self.categories = ['Utilities']
		self.keywords = ['Foo', 'Player', 'Viewer']

FooInstaller().install()
```
