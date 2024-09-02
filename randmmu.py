import logging
import random
from mmu import MMU
from page import Page

logger = logging.getLogger(__name__)


class RandMMU(MMU):
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
        # Do nothing if page is in the memory
        if page_number in self.page_table:
            return

        # Page fault
        logger.debug(f"Page fault at page {page_number}")
        self.num_page_faults += 1
        self.num_disk_reads += 1

        # Evict a page
        rand_number = random.randint(0, self.frames - 1)
        if len(self.memory) >= self.frames:
            self.memory.pop(rand_number)
            self.memory[rand_number] = page_number
        else:
            self.memory.append(page_number)

        # Load new page into memory
        self.page_table[page_number] = Page(page_number, write)
        logger.debug(f"Load new page {page_number}")

    def get_total_disk_reads(self):
        return self.num_disk_reads

    def get_total_disk_writes(self):
        return self.num_disk_writes

    def get_total_page_faults(self):
        return self.num_page_faults
