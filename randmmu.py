import random
import logging
from mmu import MMU

logger = logging.getLogger(__name__)

class RandMMU(MMU):
    def __init__(self, frames):
        self.num_disk_reads = 0
        self.num_disk_writes = 0
        self.num_page_faults = 0

        self.num_frames = frames
        self.memory = [] # Frame number: Page number

    def set_debug(self):
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    def reset_debug(self):
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)

    def read_memory(self, page_number):
        self.num_disk_reads += 1

        if page_number not in self.memory:
            logger.debug(f"Read: {page_number} - MISS")
            self.num_page_faults += 1
            self.add_page_to_memory(page_number)
        else:
            logger.debug(f"Read: {page_number} - HIT")

    def write_memory(self, page_number):
        self.num_disk_writes += 1

        if page_number not in self.memory:
            logger.debug(f"Write: {page_number} - MISS")
            self.num_page_faults += 1
            self.add_page_to_memory(page_number)
        else:
            logger.debug(f"Write: {page_number} - HIT")

    def get_total_disk_reads(self):
        return self.num_disk_reads

    def get_total_disk_writes(self):
        return self.num_disk_writes

    def get_total_page_faults(self):
        return self.num_page_faults
    
    def add_page_to_memory(self, page_number):
        """ Handle page fault """
        if len(self.memory) < self.num_frames:
            self.memory.append(page_number)
            return
        
        random_number = random.randint(0, self.num_frames - 1)
        page_number_to_replace = self.memory[random_number]
        self.memory[random_number] = page_number
        logger.debug(f"Replace {page_number_to_replace} with {page_number}")
