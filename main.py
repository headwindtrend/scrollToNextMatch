import sublime, sublime_plugin, re

class smartMatchCommand(sublime_plugin.WindowCommand):
	def run(self, backward=False, interactive=False):
		def optimize_search_term(text):
			"""Optimized transformation of selection into regex pattern for smart searching."""

			# Precompiled regex patterns (for efficiency)
			TAB_SPACE_PATTERN = re.compile(r"([^\w \t<'\"`>])")
			BACKSLASH_PATTERN = re.compile(r"([^\w\s<'\"`>])")
			QUOTE_PATTERN = re.compile(r"['\"`]")
			SPACE_PATTERN = re.compile(" +")
			TAB_PATTERN = re.compile(r"\t+")
			PROXY_PATTERN = re.compile("(?:_tAb_spAce_)+")

			# Perform substitutions efficiently
			text = TAB_SPACE_PATTERN.sub(r"_tAb_spAce_\1_tAb_spAce_", text)  # Handle spacing around symbols
			text = BACKSLASH_PATTERN.sub(r"_bAckslAsh_\1", text)  # Escape special symbols
			text = QUOTE_PATTERN.sub("['\"`]", text)  # Normalize quotes
			text = SPACE_PATTERN.sub(" *", text)  # Flexible spaces
			text = TAB_PATTERN.sub(r"\\t*", text)  # Handle tabs
			text = PROXY_PATTERN.sub(r"[\\t ]*", text)  # Kill proxies
			
			return text.replace("_bAckslAsh_", "\\")

		view = self.window.active_view()
		sel = view.sel()
		if not sel:
			return

		word_region = view.word(sel[0])  # Get selected word
		pattern = view.substr(word_region)  # Extract text
		if pattern.endswith("Command"):
			pattern = pattern[:-7]

		# Validation: Check if the word is a proper snake_case or CamelCase
		is_snake_case = re.search(r'^[a-z]+(_[a-z]+)+$', pattern)
		is_camel_case = re.search(r'^[A-Za-z][a-zA-Z]+$', pattern)

		if is_snake_case:
			# Convert snake_case to CamelCase equivalent
			camel_case_version = "".join(word.title() for word in pattern.split("_"))
			regex_pattern = r'\b' + pattern + r'\b|\b' + camel_case_version
		elif is_camel_case:
			# Convert CamelCase to snake_case equivalent
			snake_case_version = re.sub(r'([a-z])([A-Z])', r'\1_\2', pattern).lower()
			regex_pattern = r'\b' + pattern + r'|\b' + snake_case_version + r'\b' if snake_case_version != pattern.lower() else pattern
		else:
			regex_pattern = optimize_search_term(view.substr(sel[0]))
		self.window.run_command('show_panel', {
			'panel': 'find',
			'regex': True,
			'case_sensitive': False,
			'whole_word': False,
			'wrap': True,
			'in_selection': False,
			'highlight': True,
		})
		self.window.run_command('insert', {'characters': regex_pattern})
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
