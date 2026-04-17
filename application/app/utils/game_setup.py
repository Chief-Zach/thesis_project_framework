from .page import Page

class PagesObject:
    def __init__(self):
        self.pages = []

    def append(self, page: Page):
        self.pages.append(page)

    def __iter__(self):
        return iter(self.pages)