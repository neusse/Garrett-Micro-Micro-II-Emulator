# MICRO II Computer Emulator

A complete emulation of the Garrett Manufacturing MICRO II Computer, designed for education and learning computer architecture concepts.

## 🚀 Features

### Complete Hardware Emulation
- **8-bit CPU** with all 16 original instructions
- **256 words of memory** (expandable to 2048 words with bank switching)
- **Full I/O system** with 8 device addresses
- **Front panel simulation** with LED displays and switches
- **Timing accuracy** based on original 2 MHz clock

### Educational Tools
- **Assembly language support** with full assembler and disassembler
- **Interactive debugger** with single-step execution and breakpoints
- **Memory viewer** with page-by-page navigation
- **Built-in tutorials** and example programs
- **Program analysis** tools for understanding code flow

### Multiple Interfaces
- **Graphical User Interface** - Visual front panel simulation
- **Command Line Interface** - Rich text-based interaction
- **Programmable API** - Use emulator in your own Python programs

## 📋 Requirements

- Python 3.7 or higher
- tkinter (usually included with Python)
- rich (for CLI mode): `pip install rich`

## 🎯 Quick Start

### 1. Download all files
Save all the Python files in the same directory:
- `main.py` - Main entry point
- `micro2_cpu.py` - CPU implementation
- `micro2_memory.py` - Memory system
- `micro2_assembler.py` - Assembly language support
- `micro2_disassembler.py` - Disassembler
- `micro2_io.py` - I/O device simulation
- `micro2_emulator.py` - Main emulator class
- `micro2_gui.py` - GUI interface
- `micro2_cli.py` - Command line interface
- `micro2_examples.py` - Example programs and tutorials
- `micro2_tests.py` - Test suite

### 2. Install dependencies
```bash
pip install rich
```

### 3. Run the emulator
```bash
# Start GUI mode (recommended for beginners)
python main.py

# Start command line mode
python main.py --mode cli

# Run tests to verify installation
python main.py --mode test

# Get detailed help
python main.py --mode help
```

## 🖥️ User Interfaces

### GUI Mode
The graphical interface provides:
- **Front Panel Tab**: LED displays, switches, and control buttons
- **Programming Tab**: Assembly editor with sample programs
- **Memory Tab**: Memory viewer and editor
- **I/O Tab**: Device status and console simulation
- **Debug Tab**: Breakpoints, single-stepping, and analysis

### CLI Mode
The command line interface offers:
- Interactive assembly programming
- Step-by-step debugging
- Memory and register inspection
- I/O device simulation
- Batch program execution

Key CLI commands:
```
samples                 # List sample programs
samples hello_world     # Load a sample program
run                     # Execute the loaded program
step                    # Single-step execution
registers               # Show CPU state
memory                  # Show memory contents
help                    # List all commands
```

## 💻 MICRO II Architecture

### CPU Registers
- **AC** (Accumulator): 8-bit main data register
- **PC** (Program Counter): 8-bit instruction pointer
- **IR** (Instruction Register): 8-bit current instruction
- **MAR** (Memory Address Register): 8-bit memory address
- **MDR** (Memory Data Register): 8-bit memory data
- **MSR** (Memory Selection Register): 4-bit bank selector

### Instruction Set
The MICRO II has 16 instructions in 4 categories:

#### Memory Reference Instructions (with indirect addressing)
- `JMP addr` - Jump to address
- `STR addr` - Store accumulator to memory
- `ADD addr` - Add memory contents to accumulator

#### Register/Control Instructions
- `CLR` - Clear accumulator
- `CMP` - Complement accumulator (1's complement)
- `RTL` - Rotate accumulator left
- `RTR` - Rotate accumulator right
- `ORS` - OR data switches into accumulator
- `NOP` - No operation
- `HLT` - Halt execution

#### Skip Instructions
- `SNO` - Skip next instruction if no overflow
- `SNA` - Skip next instruction if accumulator non-zero
- `SZS` - Skip next instruction if sign bit = 0

#### I/O Instructions
- `SFG dev` - Skip if device flag set
- `INP dev` - Input data from device
- `OUT dev` - Output data to device

### Memory Organization
- **256 words** organized in 8 pages of 32 words each
- **Direct addressing**: 5-bit address within current page
- **Indirect addressing**: 5-bit pointer to 8-bit address (use `*` prefix)
- **Bank switching**: Up to 8 memory banks (2048 words total)

### I/O Devices
- **Device 0**: Memory bank selection
- **Device 1**: Console input
- **Device 2**: Console output
- **Device 3**: Data switches
- **Device 4**: LED display
- **Device 5**: Paper tape reader/punch
- **Devices 6-7**: Available for expansion

## 📚 Programming Examples

### Hello World
```assembly
# Output "HI" to console
CLR
ADD 10       # Load 'H' (ASCII 72)
OUT 2        # Output to console
CLR
ADD 11       # Load 'I' (ASCII 73)
OUT 2        # Output to console
HLT

# Data section
ORG 10
DATA 72      # 'H'
DATA 73      # 'I'
```

### Simple Loop
```assembly
# Count from 1 to 3
CLR
STR 20       # Initialize counter

LOOP:
ADD 21       # Add 1
STR 20       # Update counter
OUT 4        # Display on LEDs

# Check if done
STR 22       # Save count
ADD 23       # Add -3 (check for 3)
SNA          # Skip if not zero
JMP END      # Done if zero

CLR
ADD 20       # Reload counter
JMP LOOP     # Continue

END:
HLT

# Data
ORG 20
DATA 0       # Counter
DATA 1       # Increment
DATA 0       # Temp storage
DATA 253     # -3 in two's complement
```

### Indirect Addressing
```assembly
# Copy data using pointers
CLR
ADD *16      # Add data pointed to by address 16
STR *17      # Store to address pointed to by address 17
HLT

# Pointer table
ORG 16
DATA 128     # Points to address 128
DATA 129     # Points to address 129

# Data section
ORG 128
DATA 42      # Source data
DATA 0       # Destination
```

## 🧪 Testing and Development

### Run Tests
```bash
# Full test suite
python main.py --mode test

# Quick functionality test
python main.py --mode quick

# Individual module testing
python micro2_tests.py
```

### Module Organization
The emulator is organized into focused modules (~500 lines each):

- **micro2_cpu.py**: Core CPU implementation and instruction execution
- **micro2_memory.py**: Memory management and bank switching
- **micro2_assembler.py**: Assembly language parser and code generation
- **micro2_disassembler.py**: Binary to assembly conversion
- **micro2_io.py**: I/O device simulation and console interfaces
- **micro2_emulator.py**: Main emulator integration and debugging
- **micro2_gui.py**: Tkinter-based graphical interface
- **micro2_cli.py**: Rich-based command line interface
- **micro2_examples.py**: Educational programs and tutorials
- **micro2_tests.py**: Comprehensive test suite

## 🎓 Educational Use

This emulator is perfect for:

### Learning Computer Architecture
- Understand CPU instruction cycles
- Explore memory organization and addressing modes
- Learn about I/O systems and device communication
- Study assembly language programming concepts

### Assembly Programming
- Write programs in MICRO II assembly language
- Learn direct vs indirect addressing
- Practice loop programming and conditional logic
- Understand data flow and program structure

### System Analysis
- Debug programs with single-step execution
- Analyze memory usage and program flow
- Monitor I/O device interactions
- Study timing and performance characteristics

### Classroom Integration
- Built-in tutorials with step-by-step guidance
- Example programs from simple to advanced
- Interactive debugging for understanding execution
- Clear documentation and reference materials

## 🔧 Advanced Features

### Debugging Tools
- **Breakpoints**: Stop execution at specific addresses
- **Single-stepping**: Execute one instruction at a time
- **Register monitoring**: Watch CPU state changes
- **Memory inspection**: View and modify memory contents
- **Program analysis**: Understand code structure and flow

### Front Panel Simulation
- **LED displays**: Binary representation of registers
- **Data switches**: 8-bit input mechanism
- **Control buttons**: LOAD ADDRESS, LOAD DATA, DISPLAY, START/STEP
- **Status lights**: RUN, HALT, OVERFLOW indicators
- **Authentic feel**: Matches original hardware operation

### Performance Monitoring
- **Instruction counting**: Track program execution
- **Timing simulation**: Based on original 2 MHz clock
- **Execution history**: Debug and analysis support
- **Performance statistics**: Instructions per second

## 🤝 Contributing

This emulator was created for educational purposes. Feel free to:
- Extend the instruction set
- Add new I/O devices
- Create additional example programs
- Improve the user interfaces
- Add new educational features

## 📖 References

Based on the original Garrett Manufacturing MICRO II Computer documentation:
- 8-bit architecture with 16 instructions
- 256-word memory with bank expansion
- Complete I/O system with device addressing
- Front panel operation and programming

## 📄 License

This educational software is provided as-is for learning purposes. Use and modify freely for educational and non-commercial applications.

## 🆘 Support

For help:
1. Run `python main.py --mode help` for detailed usage information
2. Check the built-in tutorials and example programs
3. Use the test suite to verify correct operation
4. Refer to the MICRO II instruction reference in the GUI help system

---

**Happy programming with the MICRO II Computer Emulator!** 🚀

*Perfect for learning computer architecture, assembly programming, and system design concepts.*