"""
MICRO II Computer CPU Core Implementation
Handles registers, instruction execution, and basic CPU operations.
"""

class MICRO2_CPU:
    def __init__(self):
        # 8-bit registers
        self.ac = 0         # Accumulator (8 bits)
        self.pc = 0         # Program Counter (8 bits)
        self.ir = 0         # Instruction Register (8 bits)
        self.mar = 0        # Memory Address Register (8 bits)
        self.mdr = 0        # Memory Data Register (8 bits)
        self.msr = 0        # Memory Selection Register (4 bits)
        
        # Status flags
        self.overflow = False
        self.running = False
        self.halted = False
        
        # Front panel state
        self.data_switches = 0  # 8-bit data switches
        self.run_stop = False   # True = RUN, False = STOP
        
        # Memory reference (will be injected)
        self.memory = None
        self.io_system = None
        
        # Instruction set mapping
        self.instructions = {
            # Memory reference instructions (with indirect addressing)
            0b00: self._jmp,  # 00*AAAAA - Jump
            0b01: self._str,  # 01*AAAAA - Store AC
            0b10: self._add,  # 10*AAAAA - Add
            
            # Register/Control instructions
            0b11000000: self._clr,  # Clear AC
            0b11000001: self._cmp,  # Complement AC
            0b11000010: self._rtl,  # Rotate AC left
            0b11000011: self._rtr,  # Rotate AC right
            0b11000100: self._ors,  # OR data switches into AC
            0b11000101: self._nop,  # No operation
            0b11000110: self._hlt,  # Halt
            
            # Skip instructions
            0b11001000: self._sno,  # Skip if no overflow
            0b11001001: self._sna,  # Skip if non-zero AC
            0b11001010: self._szs,  # Skip if sign bit = 0
            
            # I/O instructions (3 MSBs + 3 LSBs for device address)
            0b11010: self._sfg,     # Skip if device flag set
            0b11100: self._inp,     # Input data from device
            0b11110: self._out,     # Output data to device
        }
    
    def reset(self):
        """Reset CPU to initial state"""
        self.ac = 0
        self.pc = 0
        self.ir = 0
        self.mar = 0
        self.mdr = 0
        self.msr = 0
        self.overflow = False
        self.running = False
        self.halted = False
        self.data_switches = 0
        self.run_stop = False
    
    def set_memory(self, memory_system):
        """Inject memory system reference"""
        self.memory = memory_system
    
    def set_io_system(self, io_system):
        """Inject I/O system reference"""
        self.io_system = io_system
    
    def execute_instruction(self):
        """Execute one instruction cycle"""
        if self.halted:
            return False
            
        # Fetch instruction
        self.mar = self.pc
        self.ir = self.memory.read(self.mar)
        self.pc = (self.pc + 1) & 0xFF
        
        # Decode and execute
        self._decode_and_execute()
        return not self.halted
    
    def _decode_and_execute(self):
        """Decode instruction and execute it"""
        # Check for memory reference instructions (2 MSBs)
        opcode = (self.ir >> 6) & 0b11
        
        if opcode in [0b00, 0b01, 0b10]:  # Memory reference instructions
            self._execute_memory_reference(opcode)
        else:
            # Check for exact instruction match first
            if self.ir in self.instructions:
                self.instructions[self.ir]()
            else:
                # Check for I/O instructions (partial match)
                io_opcode = (self.ir >> 3) & 0b11111
                if io_opcode in self.instructions:
                    self.instructions[io_opcode]()
                else:
                    # Unknown instruction - treat as NOP
                    pass
    
    def _execute_memory_reference(self, opcode):
        """Execute memory reference instruction with addressing mode"""
        indirect_bit = (self.ir >> 5) & 1
        address = self.ir & 0b11111  # 5-bit address
        
        # Handle addressing mode
        if indirect_bit:
            # Indirect addressing
            self.mdr = self.memory.read(address)
            effective_address = self.mdr
        else:
            # Direct addressing - address within current page
            current_page = (self.pc - 1) & 0xE0  # Previous PC, mask to page boundary
            effective_address = current_page | address
        
        self.mar = effective_address & 0xFF
        
        # Execute the memory reference instruction
        if opcode == 0b00:    # JMP
            self.pc = self.mar
        elif opcode == 0b01:  # STR
            self.memory.write(self.mar, self.ac)
        elif opcode == 0b10:  # ADD
            data = self.memory.read(self.mar)
            result = self.ac + data
            self.overflow = (result > 255)
            self.ac = result & 0xFF
    
    # Memory reference instructions
    def _jmp(self):
        # Handled in _execute_memory_reference
        pass
    
    def _str(self):
        # Handled in _execute_memory_reference  
        pass
    
    def _add(self):
        # Handled in _execute_memory_reference
        pass
    
    # Register/Control instructions
    def _clr(self):
        """Clear accumulator"""
        self.ac = 0
        self.overflow = False
    
    def _cmp(self):
        """Complement accumulator (1's complement)"""
        self.ac = (~self.ac) & 0xFF
    
    def _rtl(self):
        """Rotate accumulator left"""
        carry = (self.ac >> 7) & 1
        self.ac = ((self.ac << 1) | carry) & 0xFF
    
    def _rtr(self):
        """Rotate accumulator right"""
        carry = self.ac & 1
        self.ac = ((self.ac >> 1) | (carry << 7)) & 0xFF
    
    def _ors(self):
        """OR data switches into accumulator"""
        self.ac = self.ac | self.data_switches
    
    def _nop(self):
        """No operation"""
        pass
    
    def _hlt(self):
        """Halt execution"""
        self.halted = True
        self.running = False
    
    # Skip instructions
    def _sno(self):
        """Skip next instruction if no overflow"""
        if not self.overflow:
            self.pc = (self.pc + 1) & 0xFF
        self.overflow = False  # Clear overflow after test
    
    def _sna(self):
        """Skip next instruction if accumulator non-zero"""
        if self.ac != 0:
            self.pc = (self.pc + 1) & 0xFF
    
    def _szs(self):
        """Skip next instruction if sign bit = 0"""
        if (self.ac & 0x80) == 0:
            self.pc = (self.pc + 1) & 0xFF
    
    # I/O instructions
    def _sfg(self):
        """Skip if device flag set"""
        device_addr = self.ir & 0b111
        if self.io_system and self.io_system.check_flag(device_addr):
            self.pc = (self.pc + 1) & 0xFF
    
    def _inp(self):
        """Input data from device"""
        device_addr = self.ir & 0b111
        if self.io_system:
            # Data comes in complemented form and is ORed into AC
            data = self.io_system.input_data(device_addr)
            self.ac = self.ac | (~data & 0xFF)
    
    def _out(self):
        """Output data to device"""
        device_addr = self.ir & 0b111
        if self.io_system:
            if device_addr == 0:  # Special case for MSR
                self.msr = self.ac & 0x0F
                self.memory.set_bank(self.msr)
            else:
                self.io_system.output_data(device_addr, self.ac)
    
    # Front panel operations
    def load_address(self):
        """Load data switches into PC (LOAD ADDRESS button)"""
        if not self.run_stop:  # Only in STOP mode
            self.pc = self.data_switches
    
    def load_data(self):
        """Load data switches into memory at PC address (LOAD DATA button)"""
        if not self.run_stop:  # Only in STOP mode
            self.memory.write(self.pc, self.data_switches)
            self.ir = self.data_switches
            self.pc = (self.pc + 1) & 0xFF
    
    def display_memory(self):
        """Display memory contents at PC address (DISPLAY button)"""
        if not self.run_stop:  # Only in STOP mode
            self.ir = self.memory.read(self.pc)
            self.pc = (self.pc + 1) & 0xFF
    
    def start_step(self):
        """Start execution or single step (START/STEP button)"""
        if self.halted:
            return
            
        if self.run_stop:  # RUN mode
            self.running = True
        else:  # STOP mode - single step
            self.execute_instruction()
    
    def stop(self):
        """Stop execution"""
        self.running = False
    
    def set_data_switches(self, value):
        """Set the 8-bit data switch value"""
        self.data_switches = value & 0xFF
    
    def set_run_stop(self, run_mode):
        """Set run/stop switch state"""
        self.run_stop = run_mode
        if not run_mode:
            self.running = False
    
    def get_state(self):
        """Get current CPU state for display"""
        return {
            'ac': self.ac,
            'pc': self.pc,
            'ir': self.ir,
            'mar': self.mar,
            'mdr': self.mdr,
            'msr': self.msr,
            'overflow': self.overflow,
            'running': self.running,
            'halted': self.halted,
            'data_switches': self.data_switches,
            'run_stop': self.run_stop
        }
    
    def get_registers_binary(self):
        """Get registers in binary format for LED display"""
        return {
            'ac': f"{self.ac:08b}",
            'pc': f"{self.pc:08b}",
            'ir': f"{self.ir:08b}",
            'overflow': "1" if self.overflow else "0"
        }
    
    def run_continuous(self):
        """Run instructions continuously until halt or stop"""
        instruction_count = 0
        max_instructions = 10000  # Prevent infinite loops
        
        while (self.running and not self.halted and 
               instruction_count < max_instructions):
            self.execute_instruction()
            instruction_count += 1
            
        if instruction_count >= max_instructions:
            self.running = False
            return False  # Indicate potential infinite loop
        return True
