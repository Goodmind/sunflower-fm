from gi.repository import Gtk
from widgets.settings_page import SettingsPage


class ToolbarOptions(SettingsPage):
	"""Toolbar options extension class"""

	def __init__(self, parent, application):
		SettingsPage.__init__(self, parent, application, 'toolbar', _('Toolbar'))

		self._toolbar_manager = self._application.toolbar_manager

		# create list box
		container = Gtk.ScrolledWindow()
		container.set_policy(Gtk.POLICY_AUTOMATIC, Gtk.POLICY_ALWAYS)
		container.set_shadow_type(Gtk.SHADOW_IN)

		self._store = Gtk.ListStore(str, str, str, str)
		self._list = Gtk.TreeView()
		self._list.set_model(self._store)

		cell_icon = Gtk.CellRendererPixbuf()
		cell_name = Gtk.CellRendererText()
		cell_type = Gtk.CellRendererText()

		# create name column
		col_name = Gtk.TreeViewColumn(_('Name'))
		col_name.set_min_width(200)
		col_name.set_resizable(True)

		# pack and configure renderes
		col_name.pack_start(cell_icon, False)
		col_name.pack_start(cell_name, True)
		col_name.add_attribute(cell_icon, 'icon-name', 3)
		col_name.add_attribute(cell_name, 'text', 0)

		# create type column
		col_type = Gtk.TreeViewColumn(_('Type'), cell_type, markup=1)
		col_type.set_resizable(True)
		col_type.set_expand(True)

		# add columns to the list
		self._list.append_column(col_name)
		self._list.append_column(col_type)

		container.add(self._list)

		# create controls
		button_box = Gtk.HBox(False, 5)

		button_add = Gtk.Button(stock=Gtk.STOCK_ADD)
		button_add.connect('clicked', self._add_widget)

		button_delete = Gtk.Button(stock=Gtk.STOCK_DELETE)
		button_delete.connect('clicked', self._delete_widget)

		button_edit = Gtk.Button(stock=Gtk.STOCK_EDIT)
		button_edit.connect('clicked', self._edit_widget)

		image_up = Gtk.Image()
		image_up.set_from_stock(Gtk.STOCK_GO_UP, Gtk.ICON_SIZE_BUTTON)

		button_move_up = Gtk.Button(label=None)
		button_move_up.add(image_up)
		button_move_up.set_tooltip_text(_('Move Up'))
		button_move_up.connect('clicked', self._move_widget, -1)

		image_down = Gtk.Image()
		image_down.set_from_stock(Gtk.STOCK_GO_DOWN, Gtk.ICON_SIZE_BUTTON)

		button_move_down = Gtk.Button(label=None)
		button_move_down.add(image_down)
		button_move_down.set_tooltip_text(_('Move Down'))
		button_move_down.connect('clicked', self._move_widget, 1)

		# pack UI
		button_box.pack_start(button_add, False, False, 0)
		button_box.pack_start(button_delete, False, False, 0)
		button_box.pack_start(button_edit, False, False, 0)
		button_box.pack_end(button_move_down, False, False, 0)
		button_box.pack_end(button_move_up, False, False, 0)

		self.pack_start(container, True, True, 0)
		self.pack_start(button_box, False, False, 0)

	def _add_widget(self, widget, data=None):
		"""Show dialog for creating toolbar widget"""
		widget_added = self._toolbar_manager.show_create_widget_dialog(self._parent)

		if widget_added:
			# reload configuratin file
			self._load_options()

			# enable save button
			self._parent.enable_save()

	def _delete_widget(self, widget, data=None):
		"""Delete selected toolbar widget"""
		selection = self._list.get_selection()
		list_, iter_ = selection.get_selected()

		if iter_ is not None:
			# remove item from list
			list_.remove(iter_)

			# enable save button if item was removed
			self._parent.enable_save()

	def _edit_widget(self, widget, data=None):
		"""Edit selected toolbar widget"""
		selection = self._list.get_selection()
		list_, iter_ = selection.get_selected()

		if iter_ is not None:
			name = list_.get_value(iter_, 0)
			widget_type = list_.get_value(iter_, 2)

			edited = self._toolbar_manager.show_configure_widget_dialog(
			                                                name,
			                                                widget_type,
			                                                self._parent
			                                            )

			# enable save button
			if edited:
				self._parent.enable_save()

	def _move_widget(self, widget, direction):
		"""Move selected bookmark up"""
		selection = self._list.get_selection()
		list_, iter_ = selection.get_selected()

		if iter_ is not None:
			# get iter index
			index = list_.get_path(iter_)[0]

			# depending on direction, swap iters
			if (direction == -1 and index > 0) \
			or (direction == 1 and index < len(list_) - 1):
				list_.swap(iter_, list_[index + direction].iter)

			# enable save button if iters were swapped
			self._parent.enable_save()

	def _load_options(self):
		"""Load options from file"""
		toolbar_options = self._application.toolbar_options
		count = len(toolbar_options.options('widgets')) / 2

		# clear list store
		self._store.clear()

		for number in range(0, count):
			name = toolbar_options.get('widgets', 'name_{0}'.format(number))
			widget_type = toolbar_options.get('widgets', 'type_{0}'.format(number))

			data = self._toolbar_manager.get_widget_data(widget_type)

			if data is not None:
				icon = data[1]
				description = data[0]

			else:  # failsafe, display raw widget type
				icon = ''
				description = '{0} <small><i>({1})</i></small>'.format(widget_type, _('missing plugin'))

			self._store.append((name, description, widget_type, icon))

	def _save_options(self):
		"""Save settings to config file"""
		toolbar_options = self._application.toolbar_options
		count = len(self._store)

		# get section list, we'll use this
		# list to remove orphan configurations
		section_list = toolbar_options.sections()

		# clear section
		toolbar_options.remove_section('widgets')
		toolbar_options.add_section('widgets')
		section_list.pop(section_list.index('widgets'))

		# write widgets in specified order
		for number in range(0, count):
			data = self._store[number]
			toolbar_options.set('widgets', 'name_{0}'.format(number), data[0])
			toolbar_options.set('widgets', 'type_{0}'.format(number), data[2])

			# remove section from temporary list
			section_name = self._toolbar_manager.get_section_name(data[0])
			section_list.pop(section_list.index(section_name))

		# remove orphan configurations
		for section in section_list:
			toolbar_options.remove_section(section)
