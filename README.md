# xdg_soso

Installs a python script as an application on XDG compliant shells.

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
but if you don't provide it, the module name will be used.

It's probably a good idea to include an application icon, as well.

-----

The attributes which you can set include:

* comment

Displays in applications like Dash and your file explorer.

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

The icon which will be displayed in the task bar / switcher.

* mime_type

Creates a mime_type for files associated with your application.

Some examples:

> font/ttf, audio/flac, application/zip, application/x-rzip

* glob_pattern

Provide this along with "mime_type" in order to have files which match
the pattern associated with your application.

* file_icon

The icon which will be used by the file manager to decorate files which should
be associated with your application using the given "mime_type".

