from math import pi
from gi.repository import Gtk, Pango


class TitleBar(Gtk.HBox):
	"""Title bar wrapper class"""

	def __init__(self, application):
		super(TitleBar, self).__init__(homogeneous=False, spacing=1, border_width=4)

		self._application = application
		self._radius = 3
		self._control_count = 0
		self._state = Gtk.StateType.NORMAL
		self._ubuntu_coloring = self._application.options.getboolean('main', 'ubuntu_coloring')

		# connect signals
		# TODO: Bug in GI doesn't allow getting colors and custom painting
#		self.connect('expose-event', self.__expose_event)

		# top folder icon as default
		self._icon = Gtk.Image()

		# create title box
		vbox = Gtk.VBox(homogeneous=False, spacing=1)

		self._title_label = Gtk.Label()
		self._title_label.set_alignment(0, 0.5)
		self._title_label.set_use_markup(True)
		self._title_label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)

		font = Pango.FontDescription('8')
		self._subtitle_label = Gtk.Label()
		self._subtitle_label.set_alignment(0, 0.5)
		self._subtitle_label.set_use_markup(False)
		self._subtitle_label.modify_font(font)

		# pack interface
		vbox.pack_start(self._title_label, True, True, 0)
		vbox.pack_start(self._subtitle_label, False, False, 0)

		self.pack_start(self._icon, False, False, 0)
		self.pack_start(vbox, True, True, 3)

	def __get_colors(self, normal_style=False):
		"""Get copy of the style for current state"""
		if self._state is Gtk.StateType.NORMAL or normal_style:
			# normal state
			style = self._application.left_notebook.get_style().copy()
			background = style.bg[Gtk.StateType.NORMAL]
			foreground = style.fg[Gtk.StateType.NORMAL]

		else:
			# selected state
			if self._ubuntu_coloring:
				# ubuntu coloring method
				style = self._application._menu_item_tools.get_style().copy()
				background = style.bg[Gtk.StateType.NORMAL]
				foreground = style.fg[Gtk.StateType.NORMAL]

			else:
				# normal coloring method
				style = self._application.left_notebook.get_style().copy()
				background = style.bg[Gtk.StateType.SELECTED]
				foreground = style.fg[Gtk.StateType.SELECTED]

		return background, foreground

	def __get_controls_width(self):
		"""Get widget of all controls together"""
		result = 0
		spacing = self.get_spacing()

		# account for control spacing
		result += spacing * (self._control_count - 1)

		# get list of controls
		controls = self.get_children()
		total_count = len(controls)

		# get width of each control
		for index in range(total_count - self._control_count, total_count):
			result += controls[index].allocation.width

		return result
		
	def __expose_event(self, widget=None, event=None):
		"""We use this event to paint backgrounds"""
		x, y, w, h = self.allocation
		x_offset = x + w
		y_offset = y + h
		half_pi = pi / 2

		context = self.window.cairo_create()

		# clear drawing area first
		normal_color = self.__get_colors(normal_style=True)[0]
		context.set_source_rgb(
							normal_color.red_float,
							normal_color.green_float,
							normal_color.blue_float
						)
		context.rectangle(x, y, w, h)
		context.fill()

		# draw focus if needed
		if self._state is not Gtk.StateType.NORMAL:
			color = self.__get_colors()[0]
			context.set_source_rgb(
								color.red_float,
								color.green_float,
								color.blue_float
							)

			# draw rounded rectangle
			radius = self._radius + 1
			context.arc(x + radius, y + radius, radius, 2 * half_pi, 3 * half_pi)
			context.arc(x_offset - radius, y + radius, radius, 3 * half_pi, 4 * half_pi)
			context.arc(x_offset - radius, y_offset - radius, radius, 0 * half_pi, 1 * half_pi)
			context.arc(x + radius, y_offset - radius, radius, 1 * half_pi, 2 * half_pi)
			context.close_path()
			context.fill()

			# draw control space
			controls_width = self.__get_controls_width()
			border_mod = 1
			border = self.get_border_width() - border_mod

			# modify rectangle
			x = x_offset - border - controls_width - (border_mod * 2)
			y += border
			x_offset -= border
			y_offset -= border

			context.set_source_rgba(
								normal_color.red_float,
								normal_color.green_float,
								normal_color.blue_float,
								0.5
							)
			context.arc(x + self._radius, y + self._radius, self._radius, 2 * half_pi, 3 * half_pi)
			context.arc(x_offset - self._radius, y + self._radius, self._radius, 3 * half_pi, 4 * half_pi)
			context.arc(x_offset - self._radius, y_offset - self._radius, self._radius, 0 * half_pi, 1 * half_pi)
			context.arc(x + self._radius, y_offset - self._radius, self._radius, 1 * half_pi, 2 * half_pi)
			context.close_path()
			context.fill()


	def __apply_text_color(self):
		"""Apply text color for title and subtitle"""
		color = self.__get_colors()[1]

		# apply text color to labels
		self._title_label.modify_fg(Gtk.StateType.NORMAL, color)
		self._subtitle_label.modify_fg(Gtk.StateType.NORMAL, color)

	def add_control(self, widget):
		"""Add button control"""
		self._control_count += 1
		self.pack_end(widget, False, False, 0)

	def set_state(self, state):
		"""Set GTK control state for title bar"""
		self._state = state
		
		return

		# apply new colors
		self.queue_draw()
		self.__apply_text_color()

	def set_style(self, style):
		"""Set drawing style"""
		return 
	
		self._style = style
		self.queue_draw()

	def set_title(self, text):
		"""Set title text"""
		self._title_label.set_markup(text.replace('&', '&amp;'))

	def set_subtitle(self, text):
		"""Set subtitle text"""
		self._subtitle_label.set_text(text.replace('&', '&amp;'))

	def set_icon_from_name(self, icon_name):
		"""Set icon from specified name"""
		self._icon.set_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)

	def apply_settings(self):
		"""Method called when system applies new settings"""
		self._ubuntu_coloring = self._application.options.getboolean('main', 'ubuntu_coloring')

		return 
		# apply new colors
		self.queue_draw()
		self.__apply_text_color()
