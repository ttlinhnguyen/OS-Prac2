class Page:
    def __init__(self, page_number, dirty=False) -> None:
        self.page_number = page_number
        self.dirty = dirty
        self.use_bit = False