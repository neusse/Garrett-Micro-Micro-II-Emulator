"""
MICRO II Computer Test Suite
Comprehensive tests for all emulator components.
"""

import unittest
from micro2_cpu import MICRO2_CPU
from micro2_memory import MICRO2_Memory
from micro2_assembler import MICRO2_Assembler
from micro2_disassembler import MICRO2_Disassembler
from micro2_io import MICRO2_IOSystem
from micro2_emulator import MICRO2_Emulator


class TestMICRO2_CPU(unittest.TestCase):
    """Test CPU functionality"""
    
    def setUp(self):
        self.cpu = MICRO2_CPU()
        self.memory = MICRO2_Memory()
        self.io_system = MICRO2_IOSystem()
        self.cpu.set_memory(self.memory)
        self.cpu.set_io_system(self.io_system)
    
    def test_cpu_initialization(self):
        """Test CPU initial state"""
        self.assertEqual(self.cpu.ac, 0)
        self.assertEqual(self.cpu.pc, 0)
        self.assertEqual(self.cpu.ir, 0)
        self.assertFalse(self.cpu.overflow)
        self.assertFalse(self.cpu.running)
        self.assertFalse(self.cpu.halted)
    
    def test_reset(self):
        """Test CPU reset functionality"""
        self.cpu.ac = 42
        self.cpu.pc = 10
        self.cpu.overflow = True
        self.cpu.reset()
        
        self.assertEqual(self.cpu.ac, 0)
        self.assertEqual(self.cpu.pc, 0)
        self.assertFalse(self.cpu.overflow)
    
    def test_clr_instruction(self):
        """Test CLR instruction"""
        self.cpu.ac = 42
        self.cpu.overflow = True
        self.memory.write(0, 0b11000000)  # CLR instruction
        
        self.cpu.execute_instruction()
        
        self.assertEqual(self.cpu.ac, 0)
        self.assertFalse(self.cpu.overflow)
        self.assertEqual(self.cpu.pc, 1)
    
    def test_add_instruction_direct(self):
        """Test ADD instruction with direct addressing"""
        self.memory.write(0, 0b10000101)  # ADD 5 (direct)
        self.memory.write(5, 42)          # Data at address 5
        self.cpu.ac = 10
        
        self.cpu.execute_instruction()
        
        self.assertEqual(self.cpu.ac, 52)  # 10 + 42
        self.assertEqual(self.cpu.pc, 1)
    
    def test_add_instruction_indirect(self):
        """Test ADD instruction with indirect addressing"""
        self.memory.write(0, 0b10100101)  # ADD *5 (indirect)
        self.memory.write(5, 10)          # Pointer at address 5
        self.memory.write(10, 42)         # Data at address 10
        self.cpu.ac = 5
        
        self.cpu.execute_instruction()
        
        self.assertEqual(self.cpu.ac, 47)  # 5 + 42
        self.assertEqual(self.cpu.pc, 1)
    
    def test_add_overflow(self):
        """Test ADD instruction overflow"""
        self.memory.write(0, 0b10000101)  # ADD 5
        self.memory.write(5, 200)
        self.cpu.ac = 100
        
        self.cpu.execute_instruction()
        
        self.assertEqual(self.cpu.ac, 44)  # (100 + 200) & 0xFF = 44
        self.assertTrue(self.cpu.overflow)
    
    def test_str_instruction(self):
        """Test STR instruction"""
        self.memory.write(0, 0b01000101)  # STR 5
        self.cpu.ac = 42
        
        self.cpu.execute_instruction()
        
        self.assertEqual(self.memory.read(5), 42)
        self.assertEqual(self.cpu.pc, 1)
    
    def test_jmp_instruction(self):
        """Test JMP instruction"""
        self.memory.write(0, 0b00001010)  # JMP 10
        
        self.cpu.execute_instruction()
        
        self.assertEqual(self.cpu.pc, 10)
    
    def test_cmp_instruction(self):
        """Test CMP instruction"""
        self.memory.write(0, 0b11000001)  # CMP
        self.cpu.ac = 0b10101010
        
        self.cpu.execute_instruction()
        
        self.assertEqual(self.cpu.ac, 0b01010101)  # One's complement
    
    def test_rtl_instruction(self):
        """Test RTL instruction"""
        self.memory.write(0, 0b11000010)  # RTL
        self.cpu.ac = 0b10101010
        
        self.cpu.execute_instruction()
        
        self.assertEqual(self.cpu.ac, 0b01010101)  # Rotated left with wrap
    
    def test_rtr_instruction(self):
        """Test RTR instruction"""
        self.memory.write(0, 0b11000011)  # RTR
        self.cpu.ac = 0b10101010
        
        self.cpu.execute_instruction()
        
        self.assertEqual(self.cpu.ac, 0b01010101)  # Rotated right with wrap
    
    def test_sna_instruction(self):
        """Test SNA instruction"""
        # Test skip when AC non-zero
        self.memory.write(0, 0b11001001)  # SNA
        self.memory.write(1, 0b11000110)  # HLT (should be skipped)
        self.memory.write(2, 0b11000000)  # CLR
        self.cpu.ac = 42
        
        self.cpu.execute_instruction()  # Execute SNA
        self.assertEqual(self.cpu.pc, 2)  # Should skip to address 2
        
        # Test no skip when AC is zero
        self.cpu.pc = 0
        self.cpu.ac = 0
        self.cpu.execute_instruction()  # Execute SNA
        self.assertEqual(self.cpu.pc, 1)  # Should not skip
    
    def test_hlt_instruction(self):
        """Test HLT instruction"""
        self.memory.write(0, 0b11000110)  # HLT
        
        self.cpu.execute_instruction()
        
        self.assertTrue(self.cpu.halted)
        self.assertFalse(self.cpu.running)


class TestMICRO2_Memory(unittest.TestCase):
    """Test memory functionality"""
    
    def setUp(self):
        self.memory = MICRO2_Memory()
    
    def test_memory_initialization(self):
        """Test memory initial state"""
        # All memory should be zero initially
        for addr in range(256):
            self.assertEqual(self.memory.read(addr), 0)
    
    def test_basic_read_write(self):
        """Test basic memory read/write"""
        self.memory.write(42, 123)
        self.assertEqual(self.memory.read(42), 123)
    
    def test_address_wrapping(self):
        """Test address wrapping"""
        # Addresses should wrap to 8 bits
        self.memory.write(256, 42)  # Should write to address 0
        self.assertEqual(self.memory.read(0), 42)
        
        self.memory.write(300, 99)  # Should write to address 44
        self.assertEqual(self.memory.read(44), 99)
    
    def test_data_truncation(self):
        """Test data truncation to 8 bits"""
        self.memory.write(10, 256)  # Should truncate to 0
        self.assertEqual(self.memory.read(10), 0)
        
        self.memory.write(10, 511)  # Should truncate to 255
        self.assertEqual(self.memory.read(10), 255)
    
    def test_page_addressing(self):
        """Test page address calculation"""
        page, word = self.memory.get_page_address(0x55)  # 01010101
        self.assertEqual(page, 2)  # Bits 7,6,5 = 010
        self.assertEqual(word, 21)  # Bits 4,3,2,1,0 = 10101
    
    def test_program_loading(self):
        """Test program loading"""
        program = [0x11, 0x22, 0x33, 0x44]
        self.memory.load_program(program, 10)
        
        for i, instruction in enumerate(program):
            self.assertEqual(self.memory.read(10 + i), instruction)
    
    def test_memory_dump(self):
        """Test memory dump functionality"""
        self.memory.write(5, 42)
        self.memory.write(10, 99)
        
        dump = self.memory.get_memory_dump(0, 16)
        self.assertEqual(len(dump), 16)
        self.assertEqual(dump[5], 42)
        self.assertEqual(dump[10], 99)


class TestMICRO2_Assembler(unittest.TestCase):
    """Test assembler functionality"""
    
    def setUp(self):
        self.assembler = MICRO2_Assembler()
    
    def test_simple_program(self):
        """Test assembling simple program"""
        source = """
        CLR
        ADD 10
        STR 11
        HLT
        
        ORG 10
        DATA 42
        DATA 0
        """
        
        machine_code, errors = self.assembler.assemble(source)
        
        self.assertEqual(len(errors), 0)
        self.assertEqual(machine_code[0], 0b11000000)  # CLR
        self.assertEqual(machine_code[1], 0b10001010)  # ADD 10
        self.assertEqual(machine_code[2], 0b01001011)  # STR 11
        self.assertEqual(machine_code[3], 0b11000110)  # HLT
    
    def test_indirect_addressing(self):
        """Test indirect addressing assembly"""
        source = "ADD *15"
        
        machine_code, errors = self.assembler.assemble(source)
        
        self.assertEqual(len(errors), 0)
        self.assertEqual(machine_code[0], 0b10101111)  # ADD *15 (indirect bit set)
    
    def test_labels(self):
        """Test label handling"""
        source = """
        JMP LOOP
        CLR
        LOOP:
        ADD 5
        HLT
        """
        
        machine_code, errors = self.assembler.assemble(source)
        
        self.assertEqual(len(errors), 0)
        self.assertEqual(machine_code[0], 0b00000010)  # JMP 2 (LOOP address)
    
    def test_io_instructions(self):
        """Test I/O instruction assembly"""
        source = """
        INP 1
        OUT 2
        SFG 3
        """
        
        machine_code, errors = self.assembler.assemble(source)
        
        self.assertEqual(len(errors), 0)
        self.assertEqual(machine_code[0], 0b11100001)  # INP 1
        self.assertEqual(machine_code[1], 0b11110010)  # OUT 2
        self.assertEqual(machine_code[2], 0b11010011)  # SFG 3
    
    def test_data_directive(self):
        """Test DATA directive"""
        source = """
        DATA 42
        DATA 0xFF
        DATA 0b10101010
        """
        
        machine_code, errors = self.assembler.assemble(source)
        
        self.assertEqual(len(errors), 0)
        self.assertEqual(machine_code[0], 42)
        self.assertEqual(machine_code[1], 255)
        self.assertEqual(machine_code[2], 0b10101010)
    
    def test_assembly_errors(self):
        """Test error handling"""
        source = """
        INVALID_INSTRUCTION
        ADD                # Missing operand
        JMP 999           # Address too large
        """
        
        machine_code, errors = self.assembler.assemble(source)
        
        self.assertGreater(len(errors), 0)  # Should have errors


class TestMICRO2_Disassembler(unittest.TestCase):
    """Test disassembler functionality"""
    
    def setUp(self):
        self.disassembler = MICRO2_Disassembler()
    
    def test_memory_reference_instructions(self):
        """Test disassembling memory reference instructions"""
        # Direct addressing
        result = self.disassembler.disassemble_instruction(0b10001010)  # ADD 10
        self.assertEqual(result, "ADD 10")
        
        # Indirect addressing
        result = self.disassembler.disassemble_instruction(0b10101010)  # ADD *10
        self.assertEqual(result, "ADD *10")
    
    def test_register_instructions(self):
        """Test disassembling register instructions"""
        result = self.disassembler.disassemble_instruction(0b11000000)  # CLR
        self.assertEqual(result, "CLR")
        
        result = self.disassembler.disassemble_instruction(0b11000110)  # HLT
        self.assertEqual(result, "HLT")
    
    def test_io_instructions(self):
        """Test disassembling I/O instructions"""
        result = self.disassembler.disassemble_instruction(0b11100001)  # INP 1
        self.assertEqual(result, "INP 1")
        
        result = self.disassembler.disassemble_instruction(0b11110010)  # OUT 2
        self.assertEqual(result, "OUT 2")
    
    def test_unknown_instruction(self):
        """Test handling unknown instructions"""
        result = self.disassembler.disassemble_instruction(0b11111111)
        self.assertIn("DATA", result)  # Should treat as data


class TestMICRO2_IOSystem(unittest.TestCase):
    """Test I/O system functionality"""
    
    def setUp(self):
        self.io_system = MICRO2_IOSystem()
    
    def test_device_initialization(self):
        """Test I/O system initialization"""
        status = self.io_system.get_device_status()
        
        # Should have devices 1-5 installed
        self.assertIsNotNone(status[1])  # Console input
        self.assertIsNotNone(status[2])  # Console output
        self.assertIsNotNone(status[3])  # Data switches
        self.assertIsNotNone(status[4])  # LED display
        self.assertIsNotNone(status[5])  # Paper tape
    
    def test_console_io(self):
        """Test console I/O functionality"""
        # Test input
        self.io_system.queue_console_input("A")
        self.assertTrue(self.io_system.check_flag(1))
        
        data = self.io_system.input_data(1)
        self.assertEqual(data, ord('A'))
        
        # Test output
        self.io_system.output_data(2, ord('B'))
        output = self.io_system.get_console_output()
        self.assertIn('B', output)
    
    def test_data_switches(self):
        """Test data switches functionality"""
        self.io_system.set_data_switches(0b10101010)
        data = self.io_system.input_data(3)
        self.assertEqual(data, 0b10101010)
    
    def test_paper_tape(self):
        """Test paper tape functionality"""
        test_data = [1, 2, 3, 4, 5]
        self.io_system.load_paper_tape(test_data)
        
        # Should be able to read all data
        for expected in test_data:
            self.assertTrue(self.io_system.check_flag(5))
            data = self.io_system.input_data(5)
            self.assertEqual(data, expected)
        
        # Should be no more data
        self.assertFalse(self.io_system.check_flag(5))


class TestMICRO2_Emulator(unittest.TestCase):
    """Test complete emulator functionality"""
    
    def setUp(self):
        self.emulator = MICRO2_Emulator()
    
    def test_emulator_initialization(self):
        """Test emulator initialization"""
        state = self.emulator.get_system_state()
        
        self.assertEqual(state['cpu']['ac'], 0)
        self.assertEqual(state['cpu']['pc'], 0)
        self.assertFalse(state['cpu']['halted'])
    
    def test_simple_program_execution(self):
        """Test executing a simple program"""
        program = """
        CLR
        ADD 5
        STR 6
        HLT
        
        ORG 5
        DATA 42
        DATA 0
        """
        
        success, msg = self.emulator.load_assembly_program(program)
        self.assertTrue(success)
        
        success, msg = self.emulator.run_program()
        self.assertTrue(success)
        
        # Check result
        result = self.emulator.memory.read(6)
        self.assertEqual(result, 42)
        
        # Check CPU state
        state = self.emulator.cpu.get_state()
        self.assertTrue(state['halted'])
    
    def test_breakpoints(self):
        """Test breakpoint functionality"""
        program = """
        CLR
        ADD 5
        STR 6
        HLT
        
        ORG 5
        DATA 42
        DATA 0
        """
        
        self.emulator.load_assembly_program(program)
        self.emulator.set_breakpoint(2)  # Break at STR instruction
        
        success, msg = self.emulator.run_program()
        self.assertFalse(success)  # Should stop at breakpoint
        self.assertIn("Breakpoint", msg)
        
        # CPU should be at breakpoint
        self.assertEqual(self.emulator.cpu.pc, 2)
    
    def test_single_step(self):
        """Test single step functionality"""
        program = """
        CLR
        ADD 5
        HLT
        
        ORG 5
        DATA 42
        """
        
        self.emulator.load_assembly_program(program)
        
        # Step through program
        success, msg = self.emulator.single_step()  # CLR
        self.assertTrue(success)
        self.assertEqual(self.emulator.cpu.ac, 0)
        self.assertEqual(self.emulator.cpu.pc, 1)
        
        success, msg = self.emulator.single_step()  # ADD 5
        self.assertTrue(success)
        self.assertEqual(self.emulator.cpu.ac, 42)
        self.assertEqual(self.emulator.cpu.pc, 2)
        
        success, msg = self.emulator.single_step()  # HLT
        self.assertFalse(success)  # Should halt
        self.assertTrue(self.emulator.cpu.halted)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        self.emulator = MICRO2_Emulator()
    
    def test_assembly_to_execution(self):
        """Test complete workflow from assembly to execution"""
        # Complex program with loops and I/O
        program = """
        # Count from 1 to 3
        CLR
        STR 20          # Initialize counter
        
        LOOP:
        ADD 21          # Add 1
        STR 20          # Update counter
        OUT 4           # Display on LEDs
        
        # Check if done (count == 3)
        STR 22          # Save for comparison
        ADD 23          # Add -3
        SNA             # Skip if not zero
        JMP END         # Exit if zero (count == 3)
        
        CLR
        ADD 20          # Reload counter
        JMP LOOP        # Continue
        
        END:
        HLT
        
        # Data
        ORG 20
        DATA 0          # Counter
        DATA 1          # Increment
        DATA 0          # Temp
        DATA 253        # -3 in two's complement
        """
        
        # Assemble
        success, msg = self.emulator.load_assembly_program(program)
        self.assertTrue(success, f"Assembly failed: {msg}")
        
        # Execute
        success, msg = self.emulator.run_program()
        self.assertTrue(success, f"Execution failed: {msg}")
        
        # Verify results
        counter_value = self.emulator.memory.read(20)
        self.assertEqual(counter_value, 3, "Counter should reach 3")
        
        # CPU should be halted
        self.assertTrue(self.emulator.cpu.halted)
    
    def test_io_workflow(self):
        """Test I/O workflow"""
        program = """
        INP 3           # Read data switches
        CMP             # Complement the value
        OUT 2           # Output to console
        OUT 4           # Output to LEDs
        HLT
        """
        
        # Set data switches
        self.emulator.set_data_switches(0b10101010)
        
        # Run program
        self.emulator.load_assembly_program(program)
        self.emulator.run_program()
        
        # Check console output
        console_output = self.emulator.io_system.get_console_output()
        self.assertIsNotNone(console_output)


def run_all_tests():
    """Run all test suites"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestMICRO2_CPU,
        TestMICRO2_Memory,
        TestMICRO2_Assembler,
        TestMICRO2_Disassembler,
        TestMICRO2_IOSystem,
        TestMICRO2_Emulator,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


def run_quick_test():
    """Run a quick functionality test"""
    print("Running MICRO II Emulator Quick Test...")
    print("=" * 50)
    
    emulator = MICRO2_Emulator()
    
    # Test 1: Basic arithmetic
    print("Test 1: Basic Arithmetic")
    program = """
    CLR
    ADD 10
    ADD 11
    STR 12
    HLT
    
    ORG 10
    DATA 25
    DATA 17
    DATA 0
    """
    
    success, msg = emulator.load_assembly_program(program)
    if success:
        success, msg = emulator.run_program()
        if success:
            result = emulator.memory.read(12)
            expected = 42
            if result == expected:
                print(f"  ✓ PASS: 25 + 17 = {result}")
            else:
                print(f"  ✗ FAIL: Expected {expected}, got {result}")
        else:
            print(f"  ✗ FAIL: Execution error: {msg}")
    else:
        print(f"  ✗ FAIL: Assembly error: {msg}")
    
    # Test 2: Indirect addressing
    print("\nTest 2: Indirect Addressing")
    emulator.reset()
    program = """
    CLR
    ADD *10
    STR 13
    HLT
    
    ORG 10
    DATA 12      # Pointer to address 12
    DATA 0
    DATA 99      # Data at address 12
    DATA 0       # Result storage
    """
    
    success, msg = emulator.load_assembly_program(program)
    if success:
        success, msg = emulator.run_program()
        if success:
            result = emulator.memory.read(13)
            expected = 99
            if result == expected:
                print(f"  ✓ PASS: Indirect addressing result = {result}")
            else:
                print(f"  ✗ FAIL: Expected {expected}, got {result}")
        else:
            print(f"  ✗ FAIL: Execution error: {msg}")
    else:
        print(f"  ✗ FAIL: Assembly error: {msg}")
    
    # Test 3: I/O operations
    print("\nTest 3: I/O Operations")
    emulator.reset()
    emulator.set_data_switches(0b11110000)
    
    program = """
    INP 3        # Read data switches
    CMP          # Complement
    OUT 4        # Output to LEDs
    HLT
    """
    
    success, msg = emulator.load_assembly_program(program)
    if success:
        success, msg = emulator.run_program()
        if success:
            ac_value = emulator.cpu.ac
            expected = 0b00001111  # Complement of 0b11110000
            if ac_value == expected:
                print(f"  ✓ PASS: I/O operation result = {ac_value:08b}")
            else:
                print(f"  ✗ FAIL: Expected {expected:08b}, got {ac_value:08b}")
        else:
            print(f"  ✗ FAIL: Execution error: {msg}")
    else:
        print(f"  ✗ FAIL: Assembly error: {msg}")
    
    print("\n" + "=" * 50)
    print("Quick test completed!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        run_quick_test()
    else:
        success = run_all_tests()
        sys.exit(0 if success else 1)
