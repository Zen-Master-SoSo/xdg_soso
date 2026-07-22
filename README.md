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

Create an instance of XDGSetup:

```
xdg = XDGSetup(__package__, "MyModule")
xdg.comment = __doc__	# For example
```

Install your application:

```
xdg.install()
```

## Attributes

You need at a bare minumum the module name. A "friendly name" is nice to have,
but if you don't provide it, the module name will be used. It's probably a good
idea to include an application icon, as well. There are two properties which
you can use to set an application icon: "application_icon" and "generic_icon".
(See below)

-----

The attributes which you can set include:

* comment

What will be displayed in desktop applications like Dash or your file explorer.

* keywords

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

* categories

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

* application_icon

A file path to a custom icon which will be displayed in the task bar /
switcher. For example:

```python
xdg = XDGSetup('my_package', 'My Package Name')
xdg.application_icon = join(dirname(__file__), 'application-icon.svg')
```

* generic_icon

The NAME of a generic icon which you want to be displayed in the task bar /
switcher. Some generic icon names include:

> help-about, media-playback-start, document-print, emblem-important,
applications-graphics, x-office-calendar

You can use one of the generic icons like so:

```python
xdg = XDGSetup('my_package', 'My Package Name')
xdg.generic_icon = 'x-office-calendar'
```

* mime_type

Creates a NEW mime_type for files associated with your application. This
mime_type will be registered on the target system.

Some (fake) examples:

> application/my-foo, audio/my-custom-codec, text/my-text-type

* glob_pattern

Provide this along with "mime_type" in order to have files which match
the pattern associated with your application.

For example:

```python
xdg = XDGSetup('foo', 'Foo package')
xdg.mime_type = 'application/x-foo'
xdg.glob_pattern = '*.foo'
```

* file_icon

The icon which will be used by the file manager to decorate files which should
be associated with your application using the "mime_type" declared for your
application's files.

In order to use this feature, you must decide on a mime_type name and set the
"mime_type" attribute on the installer to what you have decided. (See
"mime_type" and "glob_pattern" above)

### Complete example:

```python
xdg = XDGSetup('my_package', 'Name To Call It')
xdg.comment = "A concise description of my project."
xdg.mime_type = 'x-application/foo'
xdg.glob_pattern = '*.foo'
xdg.application_icon = join(dirname(__file__), 'application-icon.svg')
xdg.file_icon = join(dirname(__file__), 'file-icon.svg')
xdg.categories = ['Utilities']
xdg.keywords = ['Foo', 'Player', 'Viewer']
xdg.install()
```
