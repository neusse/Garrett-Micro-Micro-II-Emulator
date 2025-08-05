"""
MICRO II Computer Memory System
Handles memory organization, bank switching, and memory operations.
"""

class MICRO2_Memory:
    def __init__(self):
        # Basic memory: 8 banks of 256 words each (8 bits per word)
        # Each bank has 8 pages of 32 words
        self.memory_banks = [[0] * 256 for _ in range(8)]
        self.current_bank = 0
        self.num_banks = 1  # Start with just one bank
        
        # Memory bank switch settings (from manual)
        self.bank_switches = {
            1: 0b10100010,  # AOG
            2: 0b01100010,  # BOG  
            3: 0b11100100,  # CFG
            4: 0b01101000,  # BEG
            5: 0b01101001,  # BEH
            6: 0b01101010,  # BEJ
            7: 0b01101100,  # BEL
            8: 0b01101011,  # BEK
        }
    
    def reset(self):
        """Reset memory system"""
        # Clear all memory
        for bank in self.memory_banks:
            for i in range(len(bank)):
                bank[i] = 0
        self.current_bank = 0
    
    def set_num_banks(self, num_banks):
        """Set number of active memory banks (1-8)"""
        self.num_banks = max(1, min(8, num_banks))
    
    def set_bank(self, bank_num):
        """Set current memory bank (0-7)"""
        if 0 <= bank_num < self.num_banks:
            self.current_bank = bank_num
    
    def read(self, address):
        """Read 8-bit word from memory"""
        address = address & 0xFF
        return self.memory_banks[self.current_bank][address]
    
    def write(self, address, data):
        """Write 8-bit word to memory"""
        address = address & 0xFF
        data = data & 0xFF
        self.memory_banks[self.current_bank][address] = data
    
    def get_page_address(self, address):
        """Get page number and word number from address"""
        page = (address >> 5) & 0b111    # Bits 7,6,5
        word = address & 0b11111         # Bits 4,3,2,1,0
        return page, word
    
    def load_program(self, program_data, start_address=0):
        """Load program data into memory starting at address"""
        start_address = start_address & 0xFF
        
        for i, instruction in enumerate(program_data):
            addr = (start_address + i) & 0xFF
            self.write(addr, instruction & 0xFF)
    
    def get_memory_dump(self, start_addr=0, length=256):
        """Get memory dump for display"""
        dump = []
        for i in range(length):
            addr = (start_addr + i) & 0xFF
            dump.append(self.read(addr))
        return dump
    
    def get_page_contents(self, page_num):
        """Get contents of a specific page (32 words)"""
        page_num = page_num & 0b111
        start_addr = page_num << 5
        contents = []
        
        for i in range(32):
            addr = start_addr + i
            contents.append(self.read(addr))
        
        return contents
    
    def clear_memory(self):
        """Clear all memory in current bank"""
        for i in range(256):
            self.write(i, 0)
    
    def get_memory_info(self):
        """Get memory system information"""
        return {
            'current_bank': self.current_bank,
            'num_banks': self.num_banks,
            'bank_switches': self.bank_switches.get(self.num_banks, 0),
            'total_words': self.num_banks * 256
        }
    
    def export_memory(self, filename, bank=None):
        """Export memory contents to file"""
        if bank is None:
            bank = self.current_bank
            
        try:
            with open(filename, 'w') as f:
                f.write(f"# MICRO II Memory Dump - Bank {bank}\n")
                f.write(f"# Address: Data (Binary) [Decimal]\n")
                
                for addr in range(256):
                    data = self.memory_banks[bank][addr]
                    f.write(f"{addr:08b}: {data:08b} [{data:3d}]\n")
            return True
        except Exception as e:
            print(f"Error exporting memory: {e}")
            return False
    
    def import_memory(self, filename, bank=None):
        """Import memory contents from file"""
        if bank is None:
            bank = self.current_bank
            
        try:
            with open(filename, 'r') as f:
                addr = 0
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                    
                    # Parse format: address: data
                    parts = line.split(':')
                    if len(parts) >= 2:
                        try:
                            # Extract binary data part
                            data_part = parts[1].split()[0]
                            if len(data_part) == 8 and all(c in '01' for c in data_part):
                                data = int(data_part, 2)
                                self.memory_banks[bank][addr] = data
                                addr = (addr + 1) & 0xFF
                        except ValueError:
                            continue
            return True
        except Exception as e:
            print(f"Error importing memory: {e}")
            return False


class MemoryView:
    """Helper class for memory visualization"""
    
    @staticmethod
    def format_memory_page(memory, page_num):
        """Format a memory page for display"""
        contents = memory.get_page_contents(page_num)
        lines = []
        
        lines.append(f"Page {page_num} (Addresses {page_num*32:02X}-{page_num*32+31:02X})")
        lines.append("Addr  Binary   Hex Dec")
        lines.append("-" * 20)
        
        for i, data in enumerate(contents):
            addr = page_num * 32 + i
            lines.append(f"{addr:02X}:  {data:08b} {data:02X}  {data:3d}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_memory_summary(memory):
        """Format memory summary"""
        info = memory.get_memory_info()
        lines = []
        
        lines.append(f"Memory Bank {info['current_bank']} of {info['num_banks']}")
        lines.append(f"Total Memory: {info['total_words']} words")
        lines.append(f"Bank Switches: {info['bank_switches']:08b}")
        
        # Show non-zero memory locations
        lines.append("\nNon-zero Memory Locations:")
        dump = memory.get_memory_dump()
        
        for addr, data in enumerate(dump):
            if data != 0:
                page, word = memory.get_page_address(addr)
                lines.append(f"  {addr:02X} (Page {page}, Word {word:02d}): "
                           f"{data:08b} [{data:3d}]")
        
        return "\n".join(lines)
