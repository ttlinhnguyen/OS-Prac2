import logging
import time
from mmu import MMU

logger = logging.getLogger(__name__)

class LruMMU(MMU):
    def __init__(self, frames):
        self.num_disk_reads = 0
        self.num_disk_writes = 0
        self.num_page_faults = 0
        self.frames = frames

        self.page_table = {}  # Page number: Frame number
        self.access_time = {}  # Last access time
        self.memory = []  # Frame number
        self.dirty = [] # Frame number

    def set_debug(self):
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)

    def reset_debug(self):
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.WARNING)

    def track_page_in_memory(self, page_number):
        """
        Checks if the page is in memory and updates its access time.
        Returns True if the page is in memory, False otherwise.
        """
        if page_number in self.page_table:
            # Update access time if page is in memory
            self.access_time[page_number] = time.time()
            logger.debug(f"Access Page {page_number}, updated access time.")
            return True
        return False

    def evict_page(self):
        # Find the least recently used page
        page = min(self.access_time, key=self.access_time.get)
        frame = self.page_table[page]
        logger.debug(f"Evict page {page} from frame {frame}")

        # If the page is dirty - marked as written, increment disk writes
        if frame in self.dirty:
            self.num_disk_writes += 1
            logger.debug(f"Write page {page} back to disk")

        # Remove the LRU page from memory and tables
        del self.page_table[page]
        del self.access_time[page]
        if frame in self.memory:
            del self.memory[self.memory.index(frame)]

    def read_memory(self, page_number):
        if self.track_page_in_memory(page_number):
            # Page is in memory, no need to do anything else
            return

        # Page fault: Page is not in memory
        self.num_page_faults += 1
        self.num_disk_reads += 1
        logger.debug(f"Page fault on read {page_number}")
        if len(self.page_table) >= self.frames:
            self.evict_page()

        # Find the next available frame
        frame_number = len(self.page_table)
        self.page_table[page_number] = frame_number
        self.memory.append(frame_number)
        self.access_time[page_number] = time.time()
        logger.debug(f"Loaded page {page_number} into frame {frame_number}")

    def write_memory(self, page_number):
        if self.track_page_in_memory(page_number):
            # Page is in memory, mark it as modified
            frame_number = self.page_table[page_number]
            self.memory[frame_number] = "W"
            return
        # Page fault: Page is not in memory
        self.num_page_faults += 1
        self.num_disk_reads += 1
        logger.debug(f"Page fault on write {page_number}")

        if len(self.page_table) >= self.frames:
            self.evict_page()

        # Find the next available frame
        frame_number = len(self.page_table)
        self.page_table[page_number] = frame_number
        self.memory.append(frame_number)
        self.dirty.append(frame_number) # This frame is marked as written - dirty
        self.access_time[page_number] = time.time()
        logger.debug(f"Loaded page {page_number} into frame {frame_number}")

    def get_total_disk_reads(self):
        return self.num_disk_reads

    def get_total_disk_writes(self):
        return self.num_disk_writes

    def get_total_page_faults(self):
        return self.num_page_faults
