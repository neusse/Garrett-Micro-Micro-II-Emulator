"""
MICRO II Computer Disassembler
Converts binary machine code back to assembly language.
"""

class MICRO2_Disassembler:
    def __init__(self):
        # Memory reference instruction names
        self.memory_ref_names = {
            0b00: 'JMP',
            0b01: 'STR', 
            0b10: 'ADD'
        }
        
        # Register/control instruction names
        self.register_names = {
            0b11000000: 'CLR',
            0b11000001: 'CMP',
            0b11000010: 'RTL',
            0b11000011: 'RTR',
            0b11000100: 'ORS',
            0b11000101: 'NOP',
            0b11000110: 'HLT'
        }
        
        # Skip instruction names
        self.skip_names = {
            0b11001000: 'SNO',
            0b11001001: 'SNA', 
            0b11001010: 'SZS'
        }
        
        # I/O instruction names
        self.io_names = {
            0b11010: 'SFG',
            0b11100: 'INP',
            0b11110: 'OUT'
        }
    
    def disassemble_instruction(self, instruction, address=None):
        """Disassemble a single instruction"""
        instruction = instruction & 0xFF
        
        # Check memory reference instructions first
        opcode = (instruction >> 6) & 0b11
        if opcode in self.memory_ref_names:
            return self._disassemble_memory_ref(instruction)
        
        # Check exact matches for register/control instructions
        if instruction in self.register_names:
            return self.register_names[instruction]
        
        if instruction in self.skip_names:
            return self.skip_names[instruction]
        
        # Check I/O instructions (5-bit opcode + 3-bit device address)
        io_opcode = (instruction >> 3) & 0b11111
        if io_opcode in self.io_names:
            device_addr = instruction & 0b111
            return f"{self.io_names[io_opcode]} {device_addr}"
        
        # Unknown instruction
        return f"DATA 0x{instruction:02X}  ; Unknown instruction"
    
    def _disassemble_memory_ref(self, instruction):
        """Disassemble memory reference instruction"""
        opcode = (instruction >> 6) & 0b11
        indirect_bit = (instruction >> 5) & 1
        address = instruction & 0b11111
        
        mnemonic = self.memory_ref_names[opcode]
        
        if indirect_bit:
            return f"{mnemonic} *{address}"
        else:
            return f"{mnemonic} {address}"
    
    def disassemble_program(self, machine_code, start_address=0):
        """Disassemble entire program"""
        lines = []
        
        for i, instruction in enumerate(machine_code):
            addr = (start_address + i) & 0xFF
            disasm = self.disassemble_instruction(instruction, addr)
            
            # Format with address and binary
            lines.append(f"{addr:02X}: {instruction:08b} {disasm}")
        
        return lines
    
    def disassemble_memory(self, memory, start_addr=0, length=None):
        """Disassemble memory contents"""
        if length is None:
            # Find last non-zero instruction
            length = 256
            for i in range(255, -1, -1):
                if memory.read(i) != 0:
                    length = i + 1
                    break
        
        lines = []
        lines.append("# MICRO II Disassembly")
        lines.append("# Addr: Binary    Assembly")
        lines.append("#" + "-" * 35)
        
        for addr in range(start_addr, min(start_addr + length, 256)):
            instruction = memory.read(addr)
            disasm = self.disassemble_instruction(instruction, addr)
            
            lines.append(f"{addr:02X}: {instruction:08b} {disasm}")
        
        return "\n".join(lines)
    
    def analyze_program(self, memory, start_addr=0):
        """Analyze program structure and create detailed disassembly"""
        analysis = []
        analysis.append("MICRO II Program Analysis")
        analysis.append("=" * 40)
        
        # Find program bounds
        program_end = 0
        for addr in range(256):
            if memory.read(addr) != 0:
                program_end = addr
        
        if program_end == 0:
            analysis.append("No program found in memory.")
            return "\n".join(analysis)
        
        analysis.append(f"Program size: {program_end + 1} words")
        analysis.append("")
        
        # Disassemble with analysis
        jump_targets = set()
        data_locations = set()
        
        # First pass: identify jump targets and data
        for addr in range(program_end + 1):
            instruction = memory.read(addr)
            opcode = (instruction >> 6) & 0b11
            
            if opcode == 0b00:  # JMP instruction
                indirect_bit = (instruction >> 5) & 1
                target = instruction & 0b11111
                
                if not indirect_bit:
                    # Direct jump - calculate actual target
                    current_page = addr & 0xE0
                    actual_target = current_page | target
                    jump_targets.add(actual_target)
                else:
                    # Indirect jump - target is pointer location
                    jump_targets.add(target)
        
        # Second pass: disassemble with annotations
        analysis.append("Address  Binary    Instruction     Comment")
        analysis.append("-" * 50)
        
        for addr in range(program_end + 1):
            instruction = memory.read(addr)
            disasm = self.disassemble_instruction(instruction, addr)
            
            comment = ""
            if addr in jump_targets:
                comment = "; <-- Jump target"
            
            # Check if this looks like data vs instruction
            if self._is_likely_data(instruction, addr, memory):
                comment += "; (Data)"
            
            analysis.append(f"{addr:02X}:     {instruction:08b}  {disasm:<15} {comment}")
        
        # Add memory layout summary
        analysis.append("")
        analysis.append("Memory Layout Summary:")
        analysis.append("-" * 25)
        
        for page in range(8):
            page_start = page * 32
            page_end = page_start + 31
            
            # Check if page has any content
            has_content = False
            for addr in range(page_start, min(page_end + 1, 256)):
                if memory.read(addr) != 0:
                    has_content = True
                    break
            
            if has_content:
                analysis.append(f"Page {page} ({page_start:02X}-{page_end:02X}): In use")
        
        return "\n".join(analysis)
    
    def _is_likely_data(self, instruction, address, memory):
        """Heuristic to determine if instruction is likely data"""
        # Check if this creates an invalid instruction
        opcode = (instruction >> 6) & 0b11
        
        if opcode in [0b00, 0b01, 0b10]:  # Memory reference
            return False  # These are valid
        
        if instruction in self.register_names or instruction in self.skip_names:
            return False  # Valid instructions
        
        # Check I/O instructions
        io_opcode = (instruction >> 3) & 0b11111
        if io_opcode in self.io_names:
            return False  # Valid I/O instruction
        
        # If it doesn't match any valid instruction pattern, likely data
        return True
    
    def create_listing(self, source_code, machine_code):
        """Create assembly listing with source and machine code"""
        lines = []
        lines.append("MICRO II Assembly Listing")
        lines.append("=" * 40)
        lines.append("Addr Binary    Assembly Source")
        lines.append("-" * 45)
        
        source_lines = [line.strip() for line in source_code.split('\n')]
        machine_index = 0
        
        for i, source_line in enumerate(source_lines):
            if not source_line or source_line.startswith('#'):
                lines.append(f"                    ; {source_line}")
                continue
            
            if ':' in source_line and not source_line.startswith(' '):
                # Label line
                lines.append(f"                    {source_line}")
                
                # Check if instruction on same line
                parts = source_line.split(':', 1)
                if len(parts) > 1 and parts[1].strip():
                    if machine_index < len(machine_code):
                        instruction = machine_code[machine_index]
                        disasm = self.disassemble_instruction(instruction)
                        lines.append(f"{machine_index:02X}: {instruction:08b}  {disasm}")
                        machine_index += 1
            else:
                # Regular instruction
                if machine_index < len(machine_code):
                    instruction = machine_code[machine_index]
                    disasm = self.disassemble_instruction(instruction)
                    lines.append(f"{machine_index:02X}: {instruction:08b}  {disasm:<15} ; {source_line}")
                    machine_index += 1
        
        return "\n".join(lines)


def test_disassembler():
    """Test the disassembler with sample instructions"""
    disasm = MICRO2_Disassembler()
    
    test_instructions = [
        (0b11000000, "CLR"),           # Clear AC
        (0b10010000, "ADD 16"),        # Add direct address 16
        (0b10110001, "ADD *17"),       # Add indirect address 17
        (0b00001010, "JMP 10"),        # Jump to address 10
        (0b11100001, "INP 1"),         # Input from device 1
        (0b11110010, "OUT 2"),         # Output to device 2
        (0b11000110, "HLT"),           # Halt
    ]
    
    print("Disassembler Test:")
    print("Binary     Instruction")
    print("-" * 25)
    
    for instruction, expected in test_instructions:
        result = disasm.disassemble_instruction(instruction)
        print(f"{instruction:08b} {result}")


if __name__ == "__main__":
    test_disassembler()
