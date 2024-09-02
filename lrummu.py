import logging
from mmu import MMU
from page import Page

logger = logging.getLogger(__name__)


class LruMMU(MMU):
    def __init__(self, frames):
        self.num_disk_reads = 0
        self.num_disk_writes = 0
        self.num_page_faults = 0
        self.frames = frames

        self.page_table = {}  # Page number: Page Object
        self.memory = []  # Page number

    def set_debug(self):
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)

    def reset_debug(self):
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.WARNING)

    def read_memory(self, page_number):
        self.access_memory(page_number, False)

    def write_memory(self, page_number):
        self.access_memory(page_number, True)

    def access_memory(self, page_number, write):
        # Page is already in memory
        if page_number in self.page_table:
            # Move page to the end of the memory - most recently used
            self.memory.remove(page_number)
            self.memory.append(page_number)
            if write:
                self.page_table[page_number].dirty = True
            return

        # Page fault
        logger.debug(f"Page fault at page {page_number}")
        self.num_page_faults += 1
        self.num_disk_reads += 1

        # Evict a page
        if len(self.memory) >= self.frames:
            self.evict_page()

        # Load new page into memory
        self.page_table[page_number] = Page(page_number, write)
        self.memory.append(page_number)
        logger.debug(f"Load new page {page_number}")

    def evict_page(self):
        evict_page_number = self.memory.pop(0)  # Least recently used
        evict_page = self.page_table[evict_page_number]

        # Write page to disk if page is marked as dirty/written
        if evict_page.dirty:
            self.num_disk_writes += 1
            logger.debug(f"Write page {evict_page_number} to disk")

        del self.page_table[evict_page_number]
        logger.debug(f"Evict page {evict_page_number}")

    def get_total_disk_reads(self):
        return self.num_disk_reads

    def get_total_disk_writes(self):
        return self.num_disk_writes

    def get_total_page_faults(self):
        return self.num_page_faults
