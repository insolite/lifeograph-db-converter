

class Diary:

    def __init__(self,
                 # Meta
                 tag_categories=[],
                 tags=[],
                 chapter_categories=[],
                 chapters=[],
                 themes=[],
                 default_theme=None,  # TODO: Does it?
                 last_id=None,  # TODO: Does it?
                 language=None,  # TODO: Does it?
                 startup_action=None,  # TODO: Does it?
                 last_element=None,  # TODO: Does it?
                 # Entries
                 entries=[],
                 ):
        # Meta
        self.tag_categories = tag_categories
        self.tags = tags
        self.chapter_categories = chapter_categories
        self.chapters = chapters
        self.themes = themes
        self.default_theme = default_theme
        self.last_id = last_id
        self.language = language
        self.startup_action = startup_action
        self.last_element = last_element
        # Entries
        self.entries = entries
