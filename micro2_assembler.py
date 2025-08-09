"""
MICRO II Computer Assembler
Converts assembly-like text to binary machine code.
Now supports ORG directive for setting assembly address.
"""

import re

class MICRO2_Assembler:
    def __init__(self, memory_size=256):
        # Instruction opcodes
        self.memory_ref_opcodes = {
            'JMP': 0b00,
            'STR': 0b01, 
            'ADD': 0b10
        }
        
        self.register_opcodes = {
            'CLR': 0b11000000,
            'CMP': 0b11000001,
            'RTL': 0b11000010,
            'RTR': 0b11000011,
            'ORS': 0b11000100,
            'NOP': 0b11000101,
            'HLT': 0b11000110
        }
        
        self.skip_opcodes = {
            'SNO': 0b11001000,
            'SNA': 0b11001001,
            'SZS': 0b11001010
        }
        
        self.io_opcodes = {
            'SFG': 0b11010000,
            'INP': 0b11100000,
            'OUT': 0b11110000
        }
        
        self.memory_size = memory_size
        self.labels = {}
        self.errors = []
    
    def assemble(self, source_code):
        """Assemble source code to machine code"""
        self.labels = {}
        self.errors = []
        
        lines = self._preprocess(source_code)
        sparse_code = {}  # Use dictionary internally for ORG support
        
        # First pass: collect labels and handle ORG directives
        address = 0
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Handle ORG directive
            if line.upper().startswith('ORG'):
                try:
                    parts = line.split()
                    if len(parts) != 2:
                        self.errors.append(f"Line {line_num + 1}: ORG requires one address")
                        continue
                    address = self._parse_address_value(parts[1])
                    if address >= self.memory_size:
                        self.errors.append(f"Line {line_num + 1}: ORG address {address} exceeds memory size {self.memory_size}")
                    continue
                except Exception as e:
                    self.errors.append(f"Line {line_num + 1}: ORG error - {e}")
                    continue
                
            if ':' in line and not line.startswith(' '):
                # Label definition
                label = line.split(':')[0].strip()
                self.labels[label.upper()] = address
                
                # Check if there's an instruction on the same line
                remainder = line.split(':', 1)[1].strip()
                if remainder and not remainder.upper().startswith('ORG'):
                    address += 1
            else:
                # Regular instruction
                address += 1
        
        # Second pass: generate machine code
        address = 0
        for line_num, line in enumerate(lines):
            original_line = line
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            # Handle ORG directive
            if line.upper().startswith('ORG'):
                try:
                    parts = line.split()
                    address = self._parse_address_value(parts[1])
                    continue
                except:
                    continue  # Error already recorded in first pass
            
            # Handle labels
            if ':' in line and not line.startswith(' '):
                parts = line.split(':', 1)
                if len(parts) > 1 and parts[1].strip():
                    line = parts[1].strip()
                else:
                    continue
            
            # Remove comment from code if it exists
            line = line.split('#', 1)[0].strip()
            if not line:
                continue
                
            try:
                if address >= self.memory_size:
                    self.errors.append(f"Line {line_num + 1}: Address {address} exceeds memory size {self.memory_size}")
                    continue
                    
                instruction = self._parse_instruction(line, address, line_num + 1)
                sparse_code[address] = instruction
                address += 1
            except AssemblyError as e:
                self.errors.append(f"Line {line_num + 1}: {e}")
                sparse_code[address] = 0  # Insert NOP for error
                address += 1
        
        # Convert sparse dictionary back to list format for backward compatibility
        if sparse_code:
            max_address = max(sparse_code.keys())
            machine_code = [0] * (max_address + 1)  # Initialize with zeros
            for addr, instruction in sparse_code.items():
                machine_code[addr] = instruction
        else:
            machine_code = []
        
        return machine_code, self.errors
    
    def _parse_address_value(self, operand):
        """Parse address value for ORG directive"""
        if operand.upper().startswith('0X'):
            return int(operand, 16)
        elif operand.upper().startswith('0B'):
            return int(operand, 2)
        elif operand.isdigit():
            return int(operand)
        else:
            raise AssemblyError(f"Invalid address value: {operand}")
    
    def _preprocess(self, source_code):
        """Preprocess source code - remove extra whitespace, etc."""
        lines = source_code.split('\n')
        processed = []
        
        for line in lines:
            # Remove comments (but keep # comments)
            if ';' in line:
                line = line.split(';')[0]
            
            line = line.strip()
            if line:
                processed.append(line)
        
        return processed
    
    def _parse_instruction(self, line, address, line_num):
        """Parse a single instruction line"""
        parts = line.upper().split()
        if not parts:
            raise AssemblyError("Empty instruction")
        
        mnemonic = parts[0]
        
        # Memory reference instructions
        if mnemonic in self.memory_ref_opcodes:
            if len(parts) != 2:
                raise AssemblyError(f"{mnemonic} requires one operand")
            
            operand = parts[1]
            indirect, addr = self._parse_address(operand, address)
            
            opcode = self.memory_ref_opcodes[mnemonic]
            instruction = (opcode << 6) | (indirect << 5) | (addr & 0x1F)
            return instruction
        
        # Register/control instructions
        elif mnemonic in self.register_opcodes:
            if len(parts) != 1:
                raise AssemblyError(f"{mnemonic} takes no operands")
            return self.register_opcodes[mnemonic]
        
        # Skip instructions
        elif mnemonic in self.skip_opcodes:
            if len(parts) != 1:
                raise AssemblyError(f"{mnemonic} takes no operands")
            return self.skip_opcodes[mnemonic]
        
        # I/O instructions
        elif mnemonic in self.io_opcodes:
            if len(parts) != 2:
                raise AssemblyError(f"{mnemonic} requires device address")
            
            device_addr = self._parse_device_address(parts[1])
            return self.io_opcodes[mnemonic] | device_addr
        
        # Data directive
        elif mnemonic == 'DATA':
            if len(parts) != 2:
                raise AssemblyError("DATA requires one value")
            return self._parse_data_value(parts[1])
        
        else:
            raise AssemblyError(f"Unknown instruction: {mnemonic}")
    
    def _parse_address(self, operand, current_address):
        """Parse address operand, return (indirect_flag, address)"""
        indirect = False
        
        # Check for indirect addressing indicator
        if operand.startswith('(') and operand.endswith(')'):
            indirect = True
            operand = operand[1:-1]
        elif operand.startswith('*'):
            indirect = True
            operand = operand[1:]
        
        # Parse the address
        if operand in self.labels:
            addr = self.labels[operand]
        elif operand.upper().startswith('0X'):
            addr = int(operand, 16)
        elif operand.upper().startswith('0B'):
            addr = int(operand, 2)
        elif operand.isdigit():
            addr = int(operand)
        else:
            raise AssemblyError(f"Invalid address: {operand}")
        
        # For direct addressing, address must fit in 5 bits
        if not indirect and addr > 31:
            raise AssemblyError(f"Direct address {addr} exceeds 5-bit range (0-31)")
        
        # For indirect addressing, initial address must fit in 5 bits
        if indirect and addr > 31:
            raise AssemblyError(f"Indirect address pointer {addr} exceeds 5-bit range (0-31)")
        
        return indirect, addr
    
    def _parse_device_address(self, operand):
        """Parse device address (0-7)"""
        if operand.upper().startswith('0X'):
            addr = int(operand, 16)
        elif operand.upper().startswith('0B'):
            addr = int(operand, 2)
        elif operand.isdigit():
            addr = int(operand)
        else:
            raise AssemblyError(f"Invalid device address: {operand}")
        
        if not (0 <= addr <= 7):
            raise AssemblyError(f"Device address {addr} must be 0-7")
        
        return addr
    
    def _parse_data_value(self, operand):
        """Parse data value"""
        if operand.upper().startswith('0X'):
            value = int(operand, 16)
        elif operand.upper().startswith('0B'):
            value = int(operand, 2)
        elif operand.isdigit():
            value = int(operand)
        else:
            raise AssemblyError(f"Invalid data value: {operand}")
        
        if not (0 <= value <= 255):
            raise AssemblyError(f"Data value {value} must be 0-255")
        
        return value
    
    def create_sample_programs(self):
        """Create sample programs for testing"""
        programs = {}
        
        # Simple addition program (from manual)
        programs['addition'] = """
            # Simple addition: 35 + 120 = 155
            CLR          # Clear accumulator
            ADD 16       # Add contents of address 16
            ADD 17       # Add contents of address 17  
            STR 18       # Store result in address 18
            HLT          # Halt
            
            # Data section
            ORG 16
            DATA 35      # First number
            DATA 120     # Second number
            DATA 0       # Result storage
        """
        
        # Indirect addressing example
        programs['indirect'] = """
            # Indirect addressing example
            CLR          # Clear AC
            ADD *16      # Add indirect from address 16
            ADD *17      # Add indirect from address 17
            STR 18       # Store result directly
            HLT          # Halt
            
            # Indirect address pointers
            ORG 16
            DATA 20      # Points to address 20 (changed from 128 to fit 5-bit limit)
            DATA 21      # Points to address 21 (changed from 129 to fit 5-bit limit)
            DATA 0       # Result storage
            
            # Actual data at indirect addresses
            ORG 20
            DATA 35      # First number
            DATA 120     # Second number
        """
        
        # Loop example
        programs['counter'] = """
            # Simple counter program
            CLR          # Clear accumulator
        LOOP:
            ADD 20       # Add 1 (from address 20)
            STR 21       # Store current count
            SNA          # Skip if non-zero (always true here)
            JMP LOOP     # Continue loop
            HLT          # Never reached
            
            # Data
            ORG 20
            DATA 1       # Increment value
            DATA 0       # Counter storage
        """
        
        # I/O example
        programs['io_test'] = """
            # I/O device test
            CLR          # Clear AC
            INP 1        # Input from device 1
            OUT 2        # Output to device 2
            HLT          # Halt
        """
        
        # Test ORG with gaps
        programs['org_test'] = """
            # Test ORG directive with memory gaps
            ORG 0
            CLR          # Start at address 0
            ADD 50       # Add from address 50
            STR 100      # Store at address 100
            HLT
            
            ORG 50       # Jump to address 50
            DATA 42      # Some data
            
            ORG 100      # Jump to address 100  
            DATA 0       # Result storage
            
            ORG 200      # Jump way ahead
            DATA 99      # More data
        """
        
        return programs


class AssemblyError(Exception):
    """Custom exception for assembly errors"""
    pass


def format_machine_code(machine_code, memory_size=256):
    """Format machine code for display - handles sparse memory"""
    if isinstance(machine_code, dict):
        # Sort by address for display
        sorted_addresses = sorted(machine_code.keys())
        
        lines = []
        lines.append("Addr Binary   Hex Dec")
        lines.append("-" * 18)
        
        for addr in sorted_addresses:
            instruction = machine_code[addr]
            lines.append(f"{addr:02X}: {instruction:08b} {instruction:02X}  {instruction:3d}")
        
        return "\n".join(lines)
    else:
        # Handle old format (list)
        lines = []
        lines.append("Addr Binary   Hex Dec")
        lines.append("-" * 18)
        
        for addr, instruction in enumerate(machine_code):
            lines.append(f"{addr:02X}: {instruction:08b} {instruction:02X}  {instruction:3d}")
        
        return "\n".join(lines)


def format_full_memory(machine_code, memory_size=256):
    """Format complete memory map showing gaps"""
    lines = []
    lines.append(f"Complete Memory Map (0-{memory_size-1}):")
    lines.append("Addr Binary   Hex Dec  ASCII")
    lines.append("-" * 26)
    
    for addr in range(memory_size):
        if addr in machine_code:
            instruction = machine_code[addr]
            ascii_char = chr(instruction) if 32 <= instruction <= 126 else '.'
            lines.append(f"{addr:02X}: {instruction:08b} {instruction:02X}  {instruction:3d}  '{ascii_char}'")
        else:
            lines.append(f"{addr:02X}: -------- --  ---")
    
    return "\n".join(lines)


# Test the assembler
if __name__ == "__main__":
    assembler = MICRO2_Assembler()
    programs = assembler.create_sample_programs()
    
    print("Testing MICRO II Assembler with ORG support\n")
    
    for name, program in programs.items():
        print(f"=== {name.upper()} PROGRAM ===")
        print("Source code:")
        print(program)
        print()
        
        machine_code, errors = assembler.assemble(program)
        
        if errors:
            print("ERRORS:")
            for error in errors:
                print(f"  {error}")
            print()
        
        print("Machine code:")
        print(format_machine_code(machine_code))
        print()
        
        if name == 'org_test':
            print("Full memory map showing gaps:")
            print(format_full_memory(machine_code, 50))  # Show first 50 bytes
            print()
        
        print("-" * 50)
        print()
