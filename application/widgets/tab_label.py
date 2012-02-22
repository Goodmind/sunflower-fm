import gtk
import pango

class TabLabel(gtk.EventBox):
	"""Tab label wrapper class"""

	def __init__(self, application, parent):
		gtk.EventBox.__init__(self)

		self._application = application
		self._parent = parent
		
		# initialize tab events
		self.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
		self.connect('button-release-event', self._button_release_event)

		# create interface
		self._hbox = gtk.HBox(False, 0)
		self.add(self._hbox)
		
		self._label = gtk.Label()
		self._label.set_max_width_chars(20)
		self._label.set_ellipsize(pango.ELLIPSIZE_END)

		image = gtk.Image()
		image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
		image_width, image_height = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
		image.show()

		style = gtk.RcStyle()
		style.xthickness = 0
		style.ythickness = 0

		self._button = gtk.Button()
		self._button.set_focus_on_click(False)
		self._button.add(image)
		self._button.set_relief(gtk.RELIEF_NONE)
		self._button.modify_style(style)
		self._button.connect('clicked', self._close_tab)
		self._button.set_property('no-show-all', True)
		self._button.set_size_request(image_width + 2, image_height + 2)

		# pack interface
		self._hbox.pack_start(self._label, True, True, 0)
		self._hbox.pack_start(self._button, False, False, 0)

		# show controls
		if self._application.options.getboolean('main', 'tab_close_button'):
			self._button.show()
			self._hbox.set_spacing(3)
		
		self.show_all()

	def _close_tab(self, widget, data=None):
		"""Handle clicking on close button"""
		self._application.close_tab(self._parent._notebook, self._parent)
		
	def _button_release_event(self, widget, event, data = None):
		"""
		Handle clicking on the tab itself, when middle button is pressed
		the tab is closed.
		"""
		if event.button == 2:
			self._close_tab(self._button)
			return True
		else:
			return False

	def set_text(self, text):
		"""Set label text"""
		self._label.set_text(text)

	def apply_settings(self):
		"""Apply global settings to tab label"""
		if self._application.options.getboolean('main', 'tab_close_button'):
			self._button.show()
			self._hbox.set_spacing(3)

		else:
			self._button.hide()
			self._hbox.set_spacing(0)
