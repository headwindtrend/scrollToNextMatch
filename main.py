import sublime, sublime_plugin, re

class smartMatchCommand(sublime_plugin.WindowCommand):
	def run(self, backward=False, interactive=False):
		view = self.window.active_view()
		mySearchTerm = re.sub("(?:_tAb_spAce_)+", r"[\\t ]*", re.sub(r"\t+", r"\\t*", re.sub(" +", " *", re.sub(r"['\"`]", "['\"`]", re.sub(r"([^\w\s<'\"`>])", r"_bAckslAsh_\1", re.sub(r"([^\w \t<'\"`>])", r"_tAb_spAce_\1_tAb_spAce_", view.substr(view.sel()[0]))))))).replace("_bAckslAsh_", "\\")
		self.window.run_command('show_panel', {
			'panel': 'find',
			'regex': True,
			'case_sensitive': False,
			'whole_word': False,
			'wrap': True,
			'in_selection': False,
			'highlight': True,
		})
		self.window.run_command('insert', {'characters': mySearchTerm})
		if not interactive: self.window.run_command('find_prev' if backward else 'find_next', {'close_panel': True})

class nextMatchCommand(sublime_plugin.WindowCommand):
	def run(self, backward=False, interactive=False):
		view = self.window.active_view()
		if view.sel()[0].a == view.sel()[0].b:
			view.run_command('my_word_sel')
		else: self.window.run_command('find_under_prev') if backward else self.window.run_command('find_under')

class myWordSelCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		sela = self.view.sel()[0].a
		selb = self.view.sel()[0].b
		while True:
			if selb == self.view.size() or re.search(r"[^\w\-#]", self.view.substr(sublime.Region(selb, selb+1))): break
			selb += 1
		while True:
			if sela == 0 or re.search(r"[^\w\-#]", self.view.substr(sublime.Region(sela-1, sela))): break
			sela -= 1
		if sela != self.view.sel()[0].a or selb != self.view.sel()[0].b:
			self.view.sel().clear()
			self.view.sel().add(sublime.Region(sela, selb))
