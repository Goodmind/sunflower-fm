#!/usr/bin/env python

import os
import sys
import gtk
import pango
import webbrowser
import locale
import user

from menus import Menus

from input_dialog import InputDialog
from ConfigParser import RawConfigParser

# gui imports
from about_window import AboutWindow
from options_window import OptionsWindow
from icons import IconManager
from associations import AssociationManager

# plugin imports
from plugins import *

class MainWindow(gtk.Window):
	"""Main application class"""

	# set locale for international number formatting
	locale.setlocale(locale.LC_ALL)

	# temporary options container
	options = None

	def __init__(self):
		# create main window and other widgets
		gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
		self.realize()

		self.connect("delete-event", self._destroy)

		self.set_title("Sunflower")
		#self.set_default_size(950, 450)
		self.set_icon_from_file(os.path.join(os.path.dirname(sys.argv[0]),
											'images',
											'sunflower_hi-def_64x64.png'))

		# load config
		self.load_config()

		# create other guis
		self.icon_manager = IconManager(self)
		self.menu_manager = Menus(self)
		self.associations_manager = AssociationManager()
		self.about_window = AboutWindow(self)
		self.options_window = OptionsWindow(self)

		# define local variables
		self._in_fullscreen = False

		# create menu items
		menu_bar = gtk.MenuBar()

		menu_items = (
			{
				'label': 'File',
				'submenu': (
					{
						'label': 'E_xit',
						'type': 'image',
						'stock': gtk.STOCK_QUIT,
						'callback' : self._destroy
					},
				)
			},
			{
				'label': 'Mark',
				'submenu': (
					{
						'label': '_Select all',
						'type': 'image',
						'stock': gtk.STOCK_SELECT_ALL,
						'callback': self.select_all
					},
					{
						'label': '_Unselect all',
						'callback': self.unselect_all
					},
					{
						'label': 'Invert select_ion',
						'callback': self.invert_selection
					},
					{'type': 'separator'},
					{
						'label': 'S_elect with pattern',
						'callback': self.select_with_pattern
					},
					{
						'label': 'Unselect with pa_ttern',
						'callback': self.unselect_with_pattern
					},
					{'type': 'separator'},
					{
						'label': 'Compare _directories',
						'type': 'image',
						'stock': gtk.STOCK_DIRECTORY,
					}
				)
			},
			{
				'label': 'Settings',
				'submenu': (
					{'label': 'Tool_bar'},
					{'label': 'Boo_kmarks'},
					{'type': 'separator'},
					{
						'label': 'Show _hidden files',
						'type': 'checkbox',
						'active': self.options.getboolean('main', 'show_hidden'),
						'callback': self._toggle_show_hidden_files
					},
					{
						'label': 'Show _toolbar',
						'type': 'checkbox',
					},
					{
						'label': 'Show _command bar',
						'type': 'checkbox',
						'active': self.options.getboolean('main', 'show_command_bar'),
						'callback': self._toggle_show_command_bar
					},
					{'type': 'separator'},
					{
						'label': '_Options', 'type': 'image',
						'stock': gtk.STOCK_PREFERENCES,
						'callback': self.options_window._show
					},
				)
			},
			{
				'label': 'Tools',
			},
			{
				'label': 'Help',
				'right': True,
				'submenu': (
					{
						'label': '_Home page',
						'type': 'image',
						'stock': gtk.STOCK_HOME,
						'callback': self.goto_web,
						'data': 'rcf-group.com'
					},
					{'type': 'separator'},
					{
						'label': 'File a _bug report',
						'callback': self.goto_web,
						'data': 'code.google.com/p/sunflower-fm/issues/entry'
					},
					{
						'label': 'Check for _updates',
					},
					{'type': 'separator'},
					{
						'label': '_About',
						'type': 'image',
						'stock': gtk.STOCK_ABOUT,
						'callback': self.about_window._show,
					}
				)
			},
		)

		# add items to main menu
		for item in menu_items:
			menu_bar.append(self.menu_manager.create_menu_item(item))

		# create toolbar
		self.toolbar = gtk.Toolbar()

		# create notebooks
		hbox = gtk.HBox(True, 3)

		self.left_notebook = gtk.Notebook()
		self.left_notebook.set_scrollable(True)
		self.left_notebook.connect('focus-in-event', self._transfer_focus)
		self.left_notebook.set_group_id(0)

		self.right_notebook = gtk.Notebook()
		self.right_notebook.set_scrollable(True)
		self.right_notebook.connect('focus-in-event', self._transfer_focus)
		self.right_notebook.set_group_id(0)

		hbox.pack_start(self.left_notebook, True, True, 0)
		hbox.pack_start(self.right_notebook, True, True, 0)

		# command line prompt
		hbox2 = gtk.HBox(False, 0)

		self.path_label = gtk.Label()
		self.path_label.set_alignment(1, 0.5)
		self.path_label.set_ellipsize(pango.ELLIPSIZE_MIDDLE)

		# create history list
		self.command_list = gtk.ListStore(str)

		# create autocomplete entry
		self.command_completion = gtk.EntryCompletion()
		self.command_completion.set_model(self.command_list)
		self.command_completion.set_minimum_key_length(2)
		self.command_completion.set_text_column(0)

		# create editor
		self.command_edit = gtk.Entry()
		self.command_edit.set_completion(self.command_completion)
		self.command_edit.connect('activate', self.execute_command)
		self.command_edit.connect('key-press-event', self._command_edit_key_press)

		# load history file
		self._load_history()

		hbox2.pack_start(self.path_label, True, True, 3)
		hbox2.pack_start(self.command_edit, True, True, 0)

		# command buttons bar
		self.command_bar = gtk.HBox(True, 0)

		buttons = (
				('Refresh', 'Reload active item list (F2 or CTRL+R)', self._command_reload),
				('View', 'View selected file (F3)', None),
				('Edit', 'Edit selected file (F4)', self._command_edit),
				('Copy', 'Copy selected items from active to oposite list (F5)', None),
				('Move', 'Move selected items from active to oposite list (F6)', None),
				('Create', 'Create new directory (F7)\nCreate new file (CTRL+F7)', self._command_create),
				('Delete', 'Delete selected items (F8 or Delete)', self._command_delete)
			)
		style = self.command_bar.get_style().copy()

		# create buttons and pack them
		for text, tooltip, callback in buttons:
			button = gtk.Button(label=text)

			if callback is not None:
				button.connect('clicked', callback)

			button.set_tooltip_text(tooltip)
			button.modify_bg(gtk.STATE_NORMAL, style.bg[gtk.STATE_NORMAL])
			button.modify_fg(gtk.STATE_NORMAL, style.fg[gtk.STATE_NORMAL])
			button.set_focus_on_click(False)

			button.show()

			self.command_bar.pack_start(button, True, True, 0)

		self.command_bar.set_property(
						'no-show-all',
						not self.options.getboolean('main', 'show_command_bar')
						)

		# pack gui
		vbox = gtk.VBox(False, 0)
		vbox.pack_start(menu_bar, expand=False, fill=False, padding=0)
		vbox.pack_start(self.toolbar, expand=False, fill=False, padding=0)

		vbox2 = gtk.VBox(False, 3)
		vbox2.set_border_width(3)
		vbox2.pack_start(hbox, expand=True, fill=True, padding=0)
		vbox2.pack_start(hbox2, expand=False, fill=False, padding=0)
		vbox2.pack_start(self.command_bar, expand=False, fill=False, padding=0)

		vbox.pack_start(vbox2, True, True, 0)
		self.add(vbox)

		# restore window size and position
		self._restore_window_position()

		# show widgets
		self.show_all()

	def _destroy(self, widget, data=None):
		"""Application desctructor"""

		self.save_tabs(self.left_notebook, 'tabs_left')
		self.save_tabs(self.right_notebook, 'tabs_right')

		self._save_window_position()

		self.save_config()

		gtk.main_quit()

	def _transfer_focus(self, notebook, data=None):
		"""Transfer focus from notebook to child widget in active tab"""
		selected_page = notebook.get_nth_page(notebook.get_current_page())
		selected_page._main_object.grab_focus()

	def _toggle_show_hidden_files(self, widget, data=None):
		"""Transfer option event to all the lists"""
		show_hidden = widget.get_active()
		self.options.set('main', 'show_hidden', ('off', 'on')[show_hidden])

		# update left notebook
		for index in range(0, self.left_notebook.get_n_pages()):
			page = self.left_notebook.get_nth_page(index)

			if hasattr(page, 'refresh_file_list'):
				page.refresh_file_list(widget, data)

		# update right notebook
		for index in range(0, self.right_notebook.get_n_pages()):
			page = self.right_notebook.get_nth_page(index)

			if hasattr(page, 'refresh_file_list'):
				page.refresh_file_list(widget, data)

	def _toggle_show_command_bar(self, widget, data=None):
		"""Show/hide command bar"""
		show_command_bar = widget.get_active()
		self.options.set('main', 'show_command_bar', ('off', 'on')[show_command_bar])

		if show_command_bar:
			self.command_bar.show()
		else:
			self.command_bar.hide()

	def _get_active_object(self):
		"""Return active notebook object"""
		return self._active_object

	def _set_active_object(self, object):
		"""Set active object"""
		if object is not None:
			self._active_object = object

	def _load_history(self):
		"""Load history file and populate the command list"""
		self.command_list.clear()

		try:
			# try to load our history file
			for line in file(os.path.join(user.home, self.options.get('main', 'history_file'))):
				self.command_list.append((line.strip(),))
		except:
			pass

	def _command_reload(self, widget, data=None):
		"""Handle command button click"""
		active_object = self._get_active_object()

		if hasattr(active_object, 'refresh_file_list'):
			active_object.refresh_file_list()

	def _command_edit(self, widget, data=None):
		"""Handle command button click"""
		active_object = self._get_active_object()

		if hasattr(active_object, '_edit_selected'):
			active_object._edit_selected()

	def _command_create(self, widget, data=None):
		"""Handle command button click"""
		active_object = self._get_active_object()

		if hasattr(active_object, '_create_directory'):
			active_object._create_directory()

	def _command_delete(self, widget, data=None):
		"""Handle command button click"""
		active_object = self._get_active_object()

		if hasattr(active_object, '_delete_files'):
			active_object._delete_files()

	def _command_edit_key_press(self, widget, event):
		"""Handle key press in command edit"""

		result = False

		# generate state sting based on modifier state (control, alt, shift)
		state = "%d%d%d" % (
					bool(event.state & gtk.gdk.CONTROL_MASK),
					bool(event.state & gtk.gdk.MOD1_MASK),
					bool(event.state & gtk.gdk.SHIFT_MASK)
				)

		# retrieve human readable key representation
		key_name = gtk.gdk.keyval_name(event.keyval)

		if (key_name == 'Up' or key_name == 'Escape') and state == '000':
			self._get_active_object()._main_object.grab_focus()
			result = True

		return result

	def _save_window_position(self):
		"""Save window position to config"""
		self.unfullscreen()
		self.unmaximize()
		size = self.get_size()
		position = self.get_position()
		geometry = '{0}x{1}+{2}+{3}'.format(size[0], size[1], position[0], position[1])

		self.options.set('main', 'window', geometry)

	def _restore_window_position(self):
		"""Restore window position from config string"""
		self.parse_geometry(self.options.get('main', 'window'))

	def select_all(self, widget, data=None):
		"""Select all items in active list"""
		list = self._get_active_object()

		# ensure we don't make exception on terminal tabs
		if hasattr(list, 'select_all'):
			list.select_all()

	def unselect_all(self, widget, data=None):
		"""Unselect all items in active list"""
		list = self._get_active_object()

		# ensure we don't make exception on terminal tabs
		if hasattr(list, 'unselect_all'):
			list.unselect_all()

	def invert_selection(self, widget, data=None):
		"""Invert selection in active list"""
		list = self._get_active_object()

		if hasattr(list, 'invert_selection'):
			list.invert_selection()

	def select_with_pattern(self, widget, data=None):
		"""Ask user for selection pattern and
		select matching items"""

		list = self._get_active_object()

		if hasattr(list, 'select_all'):
			# create dialog
			dialog = InputDialog(self)

			dialog.set_title('Select items')
			dialog.set_text('Selection pattern (eg.: *.jpg):')

			# get response
			response = dialog.get_response()

			# release dialog
			dialog.destroy()

			# commit selection
			if response[0] == gtk.RESPONSE_OK:
				list.select_all(response[1])

	def unselect_with_pattern(self, widget, data=None):
		"""Ask user for selection pattern and
		select matching items"""

		list = self._get_active_object()

		if hasattr(list, 'unselect_all'):
			# create dialog
			dialog = InputDialog(self)

			dialog.set_title('Unselect items')
			dialog.set_text('Selection pattern (eg.: *.jpg):')

			# get response
			response = dialog.get_response()

			# release dialog
			dialog.destroy()

			# commit selection
			if response[0] == gtk.RESPONSE_OK:
				list.unselect_all(response[1])

	def run(self):
		"""Main application loop"""

		# load tabs in the left notebook
		if not self.load_tabs(self.left_notebook, 'tabs_left'):
			self.create_tab(self.left_notebook, FileList)

		# load tabs in the right notebook
		if not self.load_tabs(self.right_notebook, 'tabs_right'):
			self.create_tab(self.right_notebook, FileList)

		gtk.main()

	def create_tab(self, notebook, plugin_class=None, data=None):
		"""Safe create tab"""
		if data is None:
			new_tab = plugin_class(self, notebook)
		else:
			new_tab = plugin_class(self, notebook, data)

		index = notebook.append_page(new_tab, new_tab._tab_label)
		new_tab._tab_index = index
		notebook.set_tab_reorderable(new_tab, True)
		notebook.set_tab_detachable(new_tab, True)

		if self.options.getboolean('main', 'focus_new_tab'):
			notebook.set_current_page(index)
			new_tab._main_object.grab_focus()

	def create_terminal_tab(self, notebook, path=None):
		"""Create terminal tab on selected notebook"""
		self.create_tab(notebook, SystemTerminal, path)

	def close_tab(self, notebook, tab_number):
		"""Safely remove tab and it's children"""

		if notebook.get_n_pages() > 1:
			object = notebook.get_nth_page(tab_number)
			notebook.remove_page(tab_number)

			del object

			object = notebook.get_nth_page(notebook.get_current_page())
			object._main_object.grab_focus()

	def next_tab(self, notebook):
		"""Select next tab on given notebook"""

		first_page = 0
		last_page = notebook.get_n_pages() - 1

		if notebook.get_current_page() == last_page:
			self.set_active_tab(notebook, first_page)
		else:
			notebook.next_page()

		page = notebook.get_nth_page(notebook.get_current_page())
		page._main_object.grab_focus()

	def previous_tab(self, notebook):
		"""Select previous tab on given notebook"""

		first_page = 0
		last_page = notebook.get_n_pages() - 1

		if notebook.get_current_page() == first_page:
			self.set_active_tab(notebook, last_page)
		else:
			notebook.prev_page()

		page = notebook.get_nth_page(notebook.get_current_page())
		page._main_object.grab_focus()

	def set_active_tab(self, notebook, tab):
		"""Set active tab number"""
		notebook.set_current_page(tab)

	def goto_web(self, widget, data=None):
		"""Open URL stored in data"""

		if data is not None:
			webbrowser.open_new_tab("http://%s" % data)

	def execute_command(self, widget, data=None):
		"""Executes system command"""
		if data is not None:
			# process custom data
			raw_command = data
		else:
			# no data is specified so we try to process command entry
			raw_command = self.command_edit.get_text()
			self.command_edit.insert_text(raw_command)
			self.command_edit.set_text('')

		handled = False
		active_object = self._get_active_object()
		command = raw_command.split(' ', 1)

		# return if we don't have anything to parse
		if len(command) < 2: return

		if command[0] == 'cd' and hasattr(active_object, 'change_path'):
			# handle CD command
			if os.path.isdir(os.path.join(active_object.path, command[1])):
				active_object.change_path(os.path.join(active_object.path, command[1]))
				active_object._main_object.grab_focus()

			handled = True

		if not handled:
			print "Unhandled command: {0}".format(command[0])

	def save_tabs(self, notebook, section):
		"""Save opened tabs"""

		self.options.remove_section(section)
		self.options.add_section(section)

		for index in range(0, notebook.get_n_pages()):
			page = notebook.get_nth_page(index)

			tab_class = page.__class__.__name__
			tab_path = page.path

			self.options.set(
							section,
							'tab_{0}'.format(index),
							'{0}:{1}'.format(tab_class, tab_path)
							)

		self.options.set('main', section, notebook.get_current_page())

	def load_tabs(self, notebook, section):
		"""Load saved tabs"""
		result = False

		if self.options.has_section(section):
			# if section exists, load it
			count = len(self.options.options(section))
			for index in range(0, count):
				data = self.options.get(section, 'tab_{0}'.format(index))

				tab_class = data.split(':', 1)[0]
				tab_path = data.split(':', 1)[1]

				self.create_tab(notebook, globals()[tab_class], tab_path)

			result = True

			# set active tab
			self.set_active_tab(notebook, self.options.getint('main', section))

		return result

	def save_config(self):
		"""Save configuration to file"""
		try:
			# try to save configuration
			config_file = os.path.join(user.home, ".sunflower")
			config = open(config_file, "w")

			self.options.write(config)

		except:
			# notify user about failure
			dialog = gtk.MessageDialog(
									self,
									gtk.DIALOG_DESTROY_WITH_PARENT,
									gtk.MESSAGE_ERROR,
									gtk.BUTTONS_OK,
									"There was an error saving configuration to "
									"file located in your home directory."
									"Make sure you have enough permissions."
									)
			dialog.run()
			dialog.destroy()

	def load_config(self):
		"""Load configuration from file located in users home directory"""

		self.options = RawConfigParser()
		config_file = os.path.join(user.home, ".sunflower")

		self.options.read(config_file)

		# set default values
		if not self.options.has_section('main'):
			self.options.add_section('main')

		# define default options
		default_options = {
				'default_editor': 'gedit "{0}" &',
				'status_text': 'Directories: %(dir_count_sel)i/%(dir_count)i, '
							   'Files: %(file_count_sel)i/%(file_count)i',
				'show_hidden': 'off',
				'show_command_bar': 'off',
				'search_modifier': '010',
				'time_format': '%H:%M %d-%m-%y',
				'focus_new_tab': 'on',
				'row_hinting': 'on',
				'selection_color': 'red',
				'tabs_left': 0,
				'tabs_right': 0,
				'history_file': '.bash_history',
				'window': '950x450',
			}

		# set default options
		for option, value in default_options.items():
			if not self.options.has_option('main', option):
				self.options.set('main', option, value)

		# save default column sizes for file list
		if not self.options.has_section('FileList'):
			self.options.add_section('FileList')
			for i, size in enumerate([200, 50, 70, 50, 100]):
				self.options.set('FileList', 'size_{0}'.format(i), size)

	def focus_oposite_list(self, widget, data=None):
		"""Sets focus on oposite item list"""

		# get current tab container
		container = self.left_notebook.get_nth_page(
											self.left_notebook.get_current_page()
										)

		if container._main_object.get_property('has-focus'):
			self.right_notebook.grab_focus()
		else:
			self.left_notebook.grab_focus()

		return True

	def update_column_sizes(self, column, sender=None):
		"""Update column size on all tabs of specified class"""

		# update left notebook
		for index in range(0, self.left_notebook.get_n_pages()):
			page = self.left_notebook.get_nth_page(index)

			if isinstance(page, sender.__class__) and page is not sender:
				page.update_column_size(column.size_id)

		# update right notebook
		for index in range(0, self.right_notebook.get_n_pages()):
			page = self.right_notebook.get_nth_page(index)

			if isinstance(page, sender.__class__) and page is not sender:
				page.update_column_size(column.size_id)

	def toggle_fullscreen(self, widget, data=None):
		"""Toggle application fullscreen"""

		if self._in_fullscreen:
			self.unfullscreen()
			self._in_fullscreen = False

		else:
			self.fullscreen()
			self._in_fullscreen = True

