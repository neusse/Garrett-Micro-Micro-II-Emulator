"""
MICRO II Computer Emulator
Main emulator class that integrates CPU, memory, and I/O systems.
"""

from micro2_cpu import MICRO2_CPU
from micro2_memory import MICRO2_Memory, MemoryView
from micro2_assembler import MICRO2_Assembler, AssemblyError, format_machine_code
from micro2_disassembler import MICRO2_Disassembler
from micro2_io import MICRO2_IOSystem

import time


class MICRO2_Emulator:
    def __init__(self):
        # Initialize subsystems
        self.cpu = MICRO2_CPU()
        self.memory = MICRO2_Memory()
        self.io_system = MICRO2_IOSystem()
        self.assembler = MICRO2_Assembler()
        self.disassembler = MICRO2_Disassembler()
        
        # Connect subsystems
        self.cpu.set_memory(self.memory)
        self.cpu.set_io_system(self.io_system)
        
        # Emulator state
        self.debug_mode = False
        self.breakpoints = set()
        self.execution_history = []
        self.max_history = 100
        
        # Timing simulation
        self.clock_frequency = 2_000_000  # 2 MHz as per manual
        self.instruction_time = 1.0 / self.clock_frequency
        
    def reset(self):
        """Reset entire emulator"""
        self.cpu.reset()
        self.memory.reset()
        self.io_system.reset_all_devices()
        self.breakpoints.clear()
        self.execution_history.clear()
    
    def load_assembly_program(self, source_code, start_address=0):
        """Load and assemble program"""
        try:
            machine_code, errors = self.assembler.assemble(source_code)
            
            if errors:
                error_msg = "Assembly errors:\n" + "\n".join(errors)
                return False, error_msg
            
            self.memory.load_program(machine_code, start_address)
            self.cpu.pc = start_address
            
            return True, f"Program loaded: {len(machine_code)} instructions"
            
        except Exception as e:
            return False, f"Assembly failed: {str(e)}"
    
    def load_binary_program(self, machine_code, start_address=0):
        """Load pre-assembled machine code"""
        self.memory.load_program(machine_code, start_address)
        self.cpu.pc = start_address
        return True, f"Binary program loaded: {len(machine_code)} instructions"
    
    def single_step(self):
        """Execute single instruction"""
        if self.cpu.halted:
            return False, "CPU is halted"
        
        # Record state before execution
        if self.debug_mode:
            state = self._capture_execution_state()
            self.execution_history.append(state)
            if len(self.execution_history) > self.max_history:
                self.execution_history.pop(0)
        
        # Check breakpoint
        if self.cpu.pc in self.breakpoints:
            return False, f"Breakpoint at address {self.cpu.pc:02X}"
        
        # Execute instruction
        success = self.cpu.execute_instruction()
        
        if not success:
            return False, "CPU halted"
        
        return True, "Instruction executed"
    
    def run_program(self, max_instructions=10000):
        """Run program until halt or breakpoint"""
        self.cpu.running = True
        instruction_count = 0
        
        while (self.cpu.running and not self.cpu.halted and 
               instruction_count < max_instructions):
            
            # Check breakpoint
            if self.cpu.pc in self.breakpoints:
                self.cpu.running = False
                return False, f"Breakpoint at address {self.cpu.pc:02X}"
            
            # Execute instruction
            if not self.cpu.execute_instruction():
                break
                
            instruction_count += 1
            
            # Simulate timing if requested
            if hasattr(self, 'simulate_timing') and self.simulate_timing:
                time.sleep(self.instruction_time)
        
        if instruction_count >= max_instructions:
            self.cpu.running = False
            return False, f"Maximum instruction limit reached ({max_instructions})"
        
        if self.cpu.halted:
            return True, f"Program completed ({instruction_count} instructions)"
        
        return True, f"Program stopped ({instruction_count} instructions)"
    
    def _capture_execution_state(self):
        """Capture current execution state for debugging"""
        return {
            'pc': self.cpu.pc,
            'instruction': self.memory.read(self.cpu.pc),
            'ac': self.cpu.ac,
            'overflow': self.cpu.overflow,
            'timestamp': time.time()
        }
    
    # Debugging features
    def set_breakpoint(self, address):
        """Set breakpoint at address"""
        address = address & 0xFF
        self.breakpoints.add(address)
    
    def clear_breakpoint(self, address):
        """Clear breakpoint at address"""
        address = address & 0xFF
        self.breakpoints.discard(address)
    
    def clear_all_breakpoints(self):
        """Clear all breakpoints"""
        self.breakpoints.clear()
    
    def get_breakpoints(self):
        """Get list of current breakpoints"""
        return sorted(list(self.breakpoints))
    
    def enable_debug_mode(self, enabled=True):
        """Enable/disable debug mode"""
        self.debug_mode = enabled
        if not enabled:
            self.execution_history.clear()
    
    def get_execution_history(self):
        """Get execution history for debugging"""
        return self.execution_history.copy()
    
    # Front panel simulation
    def press_load_address(self):
        """Simulate LOAD ADDRESS button press"""
        self.cpu.load_address()
    
    def press_load_data(self):
        """Simulate LOAD DATA button press"""
        self.cpu.load_data()
    
    def press_display(self):
        """Simulate DISPLAY button press"""
        self.cpu.display_memory()
    
    def press_start_step(self):
        """Simulate START/STEP button press"""
        if self.cpu.run_stop:
            # RUN mode - start continuous execution
            return self.run_program()
        else:
            # STOP mode - single step
            return self.single_step()
    
    def set_run_stop_switch(self, run_mode):
        """Set RUN/STOP switch"""
        self.cpu.set_run_stop(run_mode)
    
    def set_data_switches(self, value):
        """Set data switch values"""
        self.cpu.set_data_switches(value)
        # Also update I/O device
        self.io_system.set_data_switches(value)
    
    # Analysis and display methods
    def disassemble_memory(self, start_addr=0, length=None):
        """Get disassembly of memory contents"""
        return self.disassembler.disassemble_memory(self.memory, start_addr, length)
    
    def analyze_program(self):
        """Get detailed program analysis"""
        return self.disassembler.analyze_program(self.memory)
    
    def get_memory_view(self, page=None):
        """Get formatted memory view"""
        if page is not None:
            return MemoryView.format_memory_page(self.memory, page)
        else:
            return MemoryView.format_memory_summary(self.memory)
    
    def get_system_state(self):
        """Get complete system state"""
        cpu_state = self.cpu.get_state()
        memory_info = self.memory.get_memory_info()
        device_status = self.io_system.get_device_status()
        
        return {
            'cpu': cpu_state,
            'memory': memory_info,
            'io_devices': device_status,
            'breakpoints': list(self.breakpoints),
            'debug_mode': self.debug_mode
        }
    
    def export_state(self, filename):
        """Export complete emulator state"""
        try:
            import json
            state = self.get_system_state()
            
            # Add memory dump
            state['memory_dump'] = self.memory.get_memory_dump()
            
            with open(filename, 'w') as f:
                json.dump(state, f, indent=2)
            return True
        except Exception as e:
            return False
    
    def get_sample_programs(self):
        """Get sample programs for testing"""
        programs = self.assembler.create_sample_programs()
        io_programs = {}
        
        # Add I/O test programs
        io_programs['console_test'] = """
            # Console I/O test
            CLR
            INP 1        # Input from console
            OUT 2        # Echo to console output
            OUT 4        # Also display on LEDs
            HLT
        """
        
        io_programs['switch_test'] = """
            # Data switch test
            CLR
            INP 3        # Read data switches
            CMP          # Complement the value
            OUT 4        # Display on LEDs
            OUT 2        # Output to console
            HLT
        """
        
        programs.update(io_programs)
        return programs
    
    def quick_test(self):
        """Run a quick test of the emulator"""
        test_program = """
            CLR          # Clear accumulator
            ADD 10       # Add value at address 10
            STR 11       # Store result at address 11
            HLT          # Halt
            
            # Data
            ORG 10
            DATA 42      # Test value
            DATA 0       # Result storage
        """
        
        success, msg = self.load_assembly_program(test_program)
        if not success:
            return False, f"Test failed to load: {msg}"
        
        success, msg = self.run_program()
        if not success:
            return False, f"Test failed to run: {msg}"
        
        result = self.memory.read(11)
        expected = 42
        
        if result == expected:
            return True, f"Test passed: result = {result}"
        else:
            return False, f"Test failed: expected {expected}, got {result}"


# Performance monitoring
class PerformanceMonitor:
    """Monitor emulator performance"""
    
    def __init__(self):
        self.instruction_count = 0
        self.start_time = None
        self.execution_times = []
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.instruction_count = 0
        self.start_time = time.time()
        self.execution_times.clear()
    
    def record_instruction(self):
        """Record instruction execution"""
        self.instruction_count += 1
        if self.start_time:
            current_time = time.time()
            self.execution_times.append(current_time)
    
    def get_statistics(self):
        """Get performance statistics"""
        if not self.start_time:
            return "Monitoring not started"
        
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            ips = self.instruction_count / elapsed
            return f"Instructions: {self.instruction_count}, Time: {elapsed:.3f}s, IPS: {ips:.0f}"
        
        return f"Instructions: {self.instruction_count}"


if __name__ == "__main__":
    # Test the emulator
    emulator = MICRO2_Emulator()
    
    print("MICRO II Emulator Test")
    print("=" * 30)
    
    # Run quick test
    success, msg = emulator.quick_test()
    print(f"Quick test: {msg}")
    
    if success:
        print("\nFinal state:")
        state = emulator.get_system_state()
        print(f"AC: {state['cpu']['ac']:08b} ({state['cpu']['ac']})")
        print(f"PC: {state['cpu']['pc']:08b} ({state['cpu']['pc']})")
        print(f"Memory at 11: {emulator.memory.read(11)}")
