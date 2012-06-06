import gtk

from widgets.settings_page import SettingsPage


class Column:
	NAME = 0
	TITLE = 1
	PRIMARY_KEY = 2
	PRIMARY_MODS = 3
	SECONDARY_KEY = 4
	SECONDARY_MODS = 5


class AcceleratorOptions(SettingsPage):
	"""Accelerator options extension class"""

	def __init__(self, parent, application):
		SettingsPage.__init__(self, parent, application, 'accelerators', _('Key bindings'))

		# create list box
		container = gtk.ScrolledWindow()
		container.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
		container.set_shadow_type(gtk.SHADOW_IN)

		self._accels = gtk.TreeStore(str, str, int, int, int, int)

		self._list = gtk.TreeView()
		self._list.set_model(self._accels)
		self._list.set_rules_hint(True)
		self._list.set_enable_search(True)
		self._list.set_search_column(Column.TITLE)

		# create and configure cell renderers
		cell_name = gtk.CellRendererText()
		cell_primary = gtk.CellRendererAccel()
		cell_secondary = gtk.CellRendererAccel()

		cell_primary.set_property('accel-mode', gtk.CELL_RENDERER_ACCEL_MODE_OTHER)
		cell_primary.set_property('editable', True)

		cell_primary.connect('accel-edited', self.__accel_edited, True)
		cell_primary.connect('accel-cleared', self.__accel_cleared, True)

		cell_secondary.set_property('accel-mode', gtk.CELL_RENDERER_ACCEL_MODE_OTHER)
		cell_secondary.set_property('editable', True)

		cell_secondary.connect('accel-edited', self.__accel_edited, False)
		cell_secondary.connect('accel-cleared', self.__accel_cleared, False)

		# create and pack columns
		col_name = gtk.TreeViewColumn(_('Description'), cell_name, markup=Column.TITLE)
		col_name.set_min_width(200)
		col_name.set_resizable(True)

		col_primary = gtk.TreeViewColumn(
									_('Primary'),
									cell_primary,
									accel_key=Column.PRIMARY_KEY,
									accel_mods=Column.PRIMARY_MODS
								)
		col_primary.set_min_width(100)

		col_secondary = gtk.TreeViewColumn(
									_('Secondary'),
									cell_secondary,
									accel_key=Column.SECONDARY_KEY,
									accel_mods=Column.SECONDARY_MODS
								)
		col_secondary.set_min_width(100)

		self._list.append_column(col_name)
		self._list.append_column(col_primary)
		self._list.append_column(col_secondary)

		# warning label
		label_warning = gtk.Label(_(
							'<b>Note:</b> You can only edit accelerators from '
							'objects created at least once in current session. '
							'To disable accelerator press <i>Backspace</i> '
							'in assign mode.'
						))
		label_warning.set_alignment(0, 0)
		label_warning.set_use_markup(True)
		label_warning.set_line_wrap(True)
		label_warning.connect('size-allocate', self._adjust_label)

		# pack interface
		container.add(self._list)

		self.pack_start(label_warning, False, False, 0)
		self.pack_start(container, True, True, 0)

	def __accel_edited(self, widget, path, key, mods, hwcode, primary):
		"""Handle editing accelerator"""
		accel_iter = self._accels.get_iter(path)

		if accel_iter is not None:
			column_key = Column.PRIMARY_KEY if primary else Column.SECONDARY_KEY
			column_mods = Column.PRIMARY_MODS if primary else Column.SECONDARY_MODS

			# save changes to local list
			self._accels.set_value(accel_iter, column_key, key)
			self._accels.set_value(accel_iter, column_mods, mods)

			# enable save button
			self._parent.enable_save(show_restart=True)

	def __accel_cleared(self, widget, path, primary):
		"""Handle clearing accelerator"""
		accel_iter = self._accels.get_iter(path)

		if accel_iter is not None:
			column_key = Column.PRIMARY_KEY if primary else Column.SECONDARY_KEY
			column_mods = Column.PRIMARY_MODS if primary else Column.SECONDARY_MODS

			# save changes to local list
			self._accels.set_value(accel_iter, column_key, 0)
			self._accels.set_value(accel_iter, column_mods, 0)

			# enable save button
			self._parent.enable_save(show_restart=True)

	def _populate_list(self):
		"""Update accelerator list"""
		manager = self._application.accelerator_manager
		bookmarks = self._application.bookmark_options
		options = self._application.options
		groups = manager.get_groups()
		groups.sort()

		# clear accelerator list
		self._accels.clear()

		# create rename list
		replace_list = {}

		key_name = '{0}.bookmark_home'.format('item_list')
		replace_list[key_name] = _('Home directory')

		# add bookmarks to the replace list
		for number in range(1, 11):
			key_name = '{0}.{1}_{2}'.format('item_list', 'bookmark', number)
			bookmark_name = 'b_{0}'.format(number)

			if bookmarks.has_option('bookmarks', bookmark_name):
				# bookmark exists
				data = bookmarks.get('bookmarks', bookmark_name).split(';', 1)
				bookmark_value = data[0]

			else:
				# bookmark doesn't exist, add generic name
				bookmark_value = 'Bookmark #{0}'.format(number)

			replace_list[key_name] = bookmark_value

		# add methods
		for group_name in groups:
			title, methods = manager.get_group_data(group_name)

			method_names = methods.keys()
			method_names.sort()

			# add group and save iter for later use
			group_iter = self._accels.append(None, (group_name, '<b>{0}</b>'.format(title), 0, 0, 0 ,0))

			for method_name in method_names:
				# add all methods from the group
				title = methods[method_name]['title']

				# check if specified method name has a rename value
				key_name = '{0}.{1}'.format(group_name, method_name)
				if replace_list.has_key(key_name):
					title = title.format(replace_list[key_name])

				# get accelerators
				primary = manager.get_accelerator(group_name, method_name, True)
				secondary = manager.get_accelerator(group_name, method_name, False)

				# make sure we have something to display
				if primary is None:
					primary = (0, 0)

				if secondary is None:
					secondary = (0, 0)

				# append to the list
				data = (method_name, title, primary[0], primary[1], secondary[0], secondary[1])
				self._accels.append(group_iter, data)

	def _adjust_label(self, widget, data=None):
		"""Adjust label size"""
		widget.set_size_request(data.width-1, -1)

	def _load_options(self):
		"""Load options and update interface"""
		self._populate_list()

	def _save_options(self):
		"""Method called when save button is clicked"""
		manager = self._application.accelerator_manager
		
		# iterate over groups
		for row in self._accels:
			group_name = self._accels.get_value(row.iter, Column.NAME)
			children = row.iterchildren()
			
			# store accelerators for current group
			for child in children:
				name = self._accels.get_value(child.iter, Column.NAME)

				# save primary accelerator
				manager._save_accelerator(
									group_name,
									name,
									(
										self._accels.get_value(child.iter, Column.PRIMARY_KEY),
										self._accels.get_value(child.iter, Column.PRIMARY_MODS)
									),
									primary=True,
									can_overwrite=True
								)
				
				# save secondary accelerator
				manager._save_accelerator(
									group_name,
									name,
									(
										self._accels.get_value(child.iter, Column.SECONDARY_KEY),
										self._accels.get_value(child.iter, Column.SECONDARY_MODS)
									),
									primary=False,
									can_overwrite=True
								)
				
