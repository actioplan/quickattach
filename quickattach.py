
# Copyright 2010-2014 Jaap Karssenberg <jaap.karssenberg@gmail.com>
# (c) 2023 actioplan GmbH - Christophe Grévent - <git@actioplan.de>

from gi.repository import Gtk

import re
import os
from datetime import date as dateclass

from zim.fs import adapt_from_oldfs
from zim.newfs import LocalFolder
from zim.plugins import PluginClass
from zim.actions import action
from zim.config import data_file, ConfigManager
from zim.notebook import Path, Notebook, NotebookInfo, \
	resolve_notebook, build_notebook, get_notebook_list
from zim.templates import get_template
from zim.main import GtkCommand, ZIM_APPLICATION

from zim.gui.mainwindow import MainWindowExtension
from zim.gui.widgets import Dialog, ScrolledTextView, IconButton, \
	InputForm, QuestionDialog
from zim.gui.clipboard import Clipboard, SelectionClipboard
from zim.gui.notebookdialog import NotebookComboBox
import zim.datetimetz as datetime


import logging

logger = logging.getLogger('zim.plugins.quickattach')


usagehelp = '''\
usage: zim --plugin quickattach [OPTIONS]

Options:
  --help, -h             Print this help text and exit
  --notebook= URI         Select the notebook in the dialog
  --namespace= URI        Input of real name
  --basename= STRING      Take the value as basename
  --attachments= FOLDER   Import all files in FOLDER as attachments,
  --remove                If added, the attachments will be removed from the origin directory
  --journal              Determines the namespace and basename from todays date (inserts at the today journal entry...)
'''


class QuickAttachPluginCommand(GtkCommand):

	options = (
		('help', 'h', 'Print this help text and exit'),
		('notebook=', '', 'Select the corresponding notebook'),
		('namespace=', '', 'Take the value as name for the page'), 
		('basename=', '', 'Take the value as basename for the page. The page reference is composed by basename + ":" + namespace'),
		('attachments=', '', 'Import all files in FOLDER as attachments, wiki input can refer these files relatively'),
		('remove','','Removes the attachments from the attachments folder')
	)

	def parse_options(self, *args):
		self.opts['option'] = [] # allow list

		if all(not a.startswith('-') for a in args):
				if arg == 'help':
					self.opts['help'] = True
				else:
					key, value = arg.split('=', 1)
					self.opts[key] = value
		else:
			GtkCommand.parse_options(self, *args)

		self.template_options = {}

		if self.opts.get('attachments', None):
			folderpath = LocalFolder(self.pwd).get_abspath(self.opts['attachments'])
			self.opts['attachments'] = LocalFolder(folderpath)

	def run_local(self):
		# Try to run dialog from local process
		# - prevents issues where dialog pop behind other applications
		#   (desktop preventing new window of existing process to hijack focus)
		# - e.g. capturing stdin requires local process
		if self.opts.get('help'):
			print(usagehelp) # TODO handle this in the base class
		else:
			self.my_run()
		return True # Done - Don't call run() as well

	def run(self):
		# If called from primary process just run the dialog
		self.my_run()
		return True

	def my_run(self):
		if 'notebook' in self.opts:
			notebook = resolve_notebook(self.opts['notebook'])
		elif len(get_notebook_list()) == 0:
			exit()
		else:
			notebook = (get_notebook_list())[0]

		notebook, x = build_notebook(LocalFolder(notebook.uri))

		namespace=self.opts.get('namespace')
		attachments=self.opts.get('attachments')
		basename=self.opts.get('basename')
		
		if namespace is None and basename is None: 
			path = 'Journal:' + self.today_as_path()
			basename = self.today_as_path()
		elif namespace is not None and basename is not None:
			path = namespace + ':' + basename
		else:
			path = namespace or basename

		path = Path(path)
		page = notebook.get_page(path)

		if (not page.hascontent):
			page.parse('wiki',"====== " + basename + " ======")
			notebook.store_page(page)

		if attachments:
			if 'remove' in self.opts:
				self.import_attachments(notebook, path, attachments, True)	
			else:
				self.import_attachments(notebook, path, attachments, False)	

		return True

	def today_as_path(self): 
		today = datetime.date.today()
		path = today.strftime('%Y:%m:%d')
		return path

	def import_attachments(self, notebook, path, from_dir, remove):
		from_dir = adapt_from_oldfs(from_dir)
		attachments = notebook.get_attachments_dir(path)
		for file in from_dir.list_files():
			file.copyto(attachments)
			if remove:
				file.remove(False)
		

class QuickAttachlugin(PluginClass):

	plugin_info = {
		'name': _('Quick Attach'), # T: plugin name
		'description': _('''\
This plugin is used from the cli to attach quickly some files to pages programmatically. 

My usage is to jot some notes on a tablet, export the notes, take it on the PC, and import automatically the exported files to a corresponding page, typically, the journal page of today.

I took the quicknote plugin as base, added some functionalities from the journal plugin, and modified it for my purpose...
'''), # T: plugin description
		'author': 'Jaap Karssenberg, C. Grévent',
		'help': 'Plugins:Quick Attach',
	}

	#~ plugin_preferences = (
		# key, type, label, default
	#~ )
