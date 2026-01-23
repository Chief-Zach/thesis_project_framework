from .page import Page

class Pages_Object:
    def __init__(self):
        self.pages = list()

    def append(self, page: Page):
        self.pages.append(page)

    def __iter__(self):
        return iter(self.pages)