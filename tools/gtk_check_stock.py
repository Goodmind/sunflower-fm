#!/usr/bin/env python
# coding:utf-8 vi:noet:ts=4

# Script for developers. Displays all icons available for GTK.

import gtk, math

defined = [ s for s in dir( gtk ) if s.startswith( "STOCK_" ) ]
defined = [ eval( "gtk.{0}".format( s ) ) for s in defined ]
available = gtk.stock_list_ids()
defined_wrong = [ s for s in defined if s not in available ]
undefined = [ s for s in available if s not in defined ]

if not defined_wrong and not undefined :
	print( "Stock item definitions are correct." )
if defined_wrong :
	print( "Defined stock items that are not available:" )
	for s in defined_wrong :
		print( "  {0}".format( s ) )
if undefined :
	print( "Available stock items that are not defined:" )
	for s in undefined :
		print( "  {0}".format( s ) )

for s in available :
	o = gtk.Image()
	o.set_from_stock( s, gtk.ICON_SIZE_BUTTON )
	o = gtk.Button( stock = s )

def display_stock():
	wnd = gtk.Window()
	wnd.set_title( "stock icons" )
	edge = int( math.ceil( math.sqrt( len( available ) ) ) )
	table = gtk.Table( rows = edge, columns = edge )
	wnd.add( table )
	for i, s in enumerate( available ) :
		image = gtk.Image()
		image.set_from_stock( s, gtk.ICON_SIZE_BUTTON )
		button = gtk.Button()
		button.set_image( image )
		button.show()
		button.set_tooltip_text( s )
		row = i % edge
		col = i / edge
		table.attach( button, row, row + 1, col, col + 1 )
	table.show()
	wnd.show()

def display_named():
	# List of named "Theme Icons"
	# from http://developer.gnome.org/icon-naming-spec/
	l = [
		'address-book-new',
		'application-exit',
		'appointment-new',
		'call-start',
		'call-stop',
		'contact-new',
		'document-new',
		'document-open',
		'document-open-recent',
		'document-page-setup',
		'document-print',
		'document-print-preview',
		'document-properties',
		'document-revert',
		'document-save',
		'document-save-as',
		'document-send',
		'edit-clear',
		'edit-copy',
		'edit-cut',
		'edit-delete',
		'edit-find',
		'edit-find-replace',
		'edit-paste',
		'edit-redo',
		'edit-select-all',
		'edit-undo',
		'folder-new',
		'format-indent-less',
		'format-indent-more',
		'format-justify-center',
		'format-justify-fill',
		'format-justify-left',
		'format-justify-right',
		'format-text-direction-ltr',
		'format-text-direction-rtl',
		'format-text-bold',
		'format-text-italic',
		'format-text-underline',
		'format-text-strikethrough',
		'go-bottom',
		'go-down',
		'go-first',
		'go-home',
		'go-jump',
		'go-last',
		'go-next',
		'go-previous',
		'go-top',
		'go-up',
		'help-about',
		'help-contents',
		'help-faq',
		'insert-image',
		'insert-link',
		'insert-object',
		'insert-text',
		'list-add',
		'list-remove',
		'mail-forward',
		'mail-mark-important',
		'mail-mark-junk',
		'mail-mark-notjunk',
		'mail-mark-read',
		'mail-mark-unread',
		'mail-message-new',
		'mail-reply-all',
		'mail-reply-sender',
		'mail-send',
		'mail-send-receive',
		'media-eject',
		'media-playback-pause',
		'media-playback-start',
		'media-playback-stop',
		'media-record',
		'media-seek-backward',
		'media-seek-forward',
		'media-skip-backward',
		'media-skip-forward',
		'object-flip-horizontal',
		'object-flip-vertical',
		'object-rotate-left',
		'object-rotate-right',
		'process-stop',
		'system-lock-screen',
		'system-log-out',
		'system-run',
		'system-search',
		'system-reboot',
		'system-shutdown',
		'tools-check-spelling',
		'view-fullscreen',
		'view-refresh',
		'view-restore',
		'view-sort-ascending',
		'view-sort-descending',
		'window-close',
		'window-new',
		'zoom-fit-best',
		'zoom-in',
		'zoom-original',
		'zoom-out',
		'process-working',
		'accessories-calculator',
		'accessories-character-map',
		'accessories-dictionary',
		'accessories-text-editor',
		'help-browser',
		'multimedia-volume-control',
		'preferences-desktop-accessibility',
		'preferences-desktop-font',
		'preferences-desktop-keyboard',
		'preferences-desktop-locale',
		'preferences-desktop-multimedia',
		'preferences-desktop-screensaver',
		'preferences-desktop-theme',
		'preferences-desktop-wallpaper',
		'system-file-manager',
		'system-software-install',
		'system-software-update',
		'utilities-system-monitor',
		'utilities-terminal',
		'applications-accessories',
		'applications-development',
		'applications-engineering',
		'applications-games',
		'applications-graphics',
		'applications-internet',
		'applications-multimedia',
		'applications-office',
		'applications-other',
		'applications-science',
		'applications-system',
		'applications-utilities',
		'preferences-desktop',
		'preferences-desktop-peripherals',
		'preferences-desktop-personal',
		'preferences-other',
		'preferences-system',
		'preferences-system-network',
		'system-help',
		'audio-card',
		'audio-input-microphone',
		'battery',
		'camera-photo',
		'camera-video',
		'camera-web',
		'computer',
		'drive-harddisk',
		'drive-optical',
		'drive-removable-media',
		'input-gaming',
		'input-keyboard',
		'input-mouse',
		'input-tablet',
		'media-flash',
		'media-floppy',
		'media-optical',
		'media-tape',
		'modem',
		'multimedia-player',
		'network-wired',
		'network-wireless',
		'pda',
		'phone',
		'printer',
		'scanner',
		'video-display',
		'emblem-default',
		'emblem-documents',
		'emblem-downloads',
		'emblem-favorite',
		'emblem-important',
		'emblem-mail',
		'emblem-photos',
		'emblem-readonly',
		'emblem-shared',
		'emblem-symbolic-link',
		'emblem-synchronized',
		'emblem-system',
		'emblem-unreadable',
		'face-angel',
		'face-angry',
		'face-cool',
		'face-crying',
		'face-devilish',
		'face-embarrassed',
		'face-kiss',
		'face-laugh',
		'face-monkey',
		'face-plain',
		'face-raspberry',
		'face-sad',
		'face-sick',
		'face-smile',
		'face-smile-big',
		'face-smirk',
		'face-surprise',
		'face-tired',
		'face-uncertain',
		'face-wink',
		'face-worried',
		'application-x-executable',
		'audio-x-generic',
		'font-x-generic',
		'image-x-generic',
		'package-x-generic',
		'text-html',
		'text-x-generic',
		'text-x-generic-template',
		'text-x-script',
		'video-x-generic',
		'x-office-address-book',
		'x-office-calendar',
		'x-office-document',
		'x-office-presentation',
		'x-office-spreadsheet',
		'folder',
		'folder-remote',
		'network-server',
		'network-workgroup',
		'start-here',
		'user-bookmarks',
		'user-desktop',
		'user-home',
		'user-trash',
		'appointment-missed',
		'appointment-soon',
		'audio-volume-high',
		'audio-volume-low',
		'audio-volume-medium',
		'audio-volume-muted',
		'battery-caution',
		'battery-low',
		'dialog-error',
		'dialog-information',
		'dialog-password',
		'dialog-question',
		'dialog-warning',
		'folder-drag-accept',
		'folder-open',
		'folder-visiting',
		'image-loading',
		'image-missing',
		'mail-attachment',
		'mail-unread',
		'mail-read',
		'mail-replied',
		'mail-signed',
		'mail-signed-verified',
		'media-playlist-repeat',
		'media-playlist-shuffle',
		'network-error',
		'network-idle',
		'network-offline',
		'network-receive',
		'network-transmit',
		'network-transmit-receive',
		'printer-error',
		'printer-printing',
		'security-high',
		'security-medium',
		'security-low',
		'software-update-available',
		'software-update-urgent',
		'sync-error',
		'sync-synchronizing',
		'task-due',
		'task-past-due',
		'user-available',
		'user-away',
		'user-idle',
		'user-offline',
		'user-trash-full',
		'weather-clear',
		'weather-clear-night',
		'weather-few-clouds',
		'weather-few-clouds-night',
		'weather-fog',
		'weather-overcast',
		'weather-severe-alert',
		'weather-showers',
		'weather-showers-scattered',
		'weather-snow',
		'weather-storm' ]
	wnd = gtk.Window()
	wnd.set_title( "named icons" )
	edge = int( math.ceil( math.sqrt( len( l ) ) ) )
	table = gtk.Table( rows = edge, columns = edge )
	wnd.add( table )
	for i, s in enumerate( l ) :
		image = gtk.Image()
		image.set_from_icon_name( s, gtk.ICON_SIZE_BUTTON )
		button = gtk.Button()
		button.set_image( image )
		button.show()
		button.set_tooltip_text( s )
		row = i % edge
		col = i / edge
		table.attach( button, row, row + 1, col, col + 1 )
	table.show()
	wnd.show()

display_stock()
display_named()
gtk.main()

