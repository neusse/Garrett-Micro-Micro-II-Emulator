#!/usr/bin/env python3
"""
MICRO II Computer Emulator
Main entry point for the MICRO II Computer Emulator

Usage:
    python main.py [--mode MODE] [--help]
    
Modes:
    gui     - Start graphical user interface (default)
    cli     - Start command line interface  
    test    - Run test suite
    quick   - Run quick functionality test
    help    - Show detailed help and examples

Author: Claude (Anthropic)
Based on: Garrett Manufacturing MICRO II Computer
"""

import sys
import argparse
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    # Check for tkinter (usually included with Python)
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
    
    # Check for rich (for CLI pretty printing)
    try:
        import rich
    except ImportError:
        missing_deps.append("rich")
    
    if missing_deps:
        print("Missing dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nInstall missing dependencies:")
        if "rich" in missing_deps:
            print("  pip install rich")
        if "tkinter" in missing_deps:
            print("  tkinter is usually included with Python.")
            print("  On Ubuntu/Debian: sudo apt-get install python3-tk")
            print("  On CentOS/RHEL: sudo yum install tkinter")
        
        return False
    
    return True

def show_welcome():
    """Show welcome message and system info"""
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                          MICRO II Computer Emulator                          ║
    ║                                                                              ║
    ║  A complete emulation of the Garrett Manufacturing MICRO II Computer        ║
    ║  * 8-bit CPU with 16 instructions                                          ║
    ║  * 256 words of memory (expandable to 2048)                                ║
    ║  * Full I/O system simulation                                               ║
    ║  * Assembly language support                                                ║
    ║  * Educational tutorials and examples                                       ║
    ║                                                                              ║
    ║  Perfect for learning computer architecture and assembly programming!       ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)

def show_help():
    """Show detailed help information"""
    show_welcome()
    
    print("""
USAGE MODES:
    
1. GUI Mode (Recommended for beginners):
   python main.py --mode gui
   
   Features:
   - Visual front panel with LED displays
   - Built-in assembly editor with syntax highlighting  
   - Memory viewer and debugger
   - I/O device simulation
   - Sample programs and tutorials
   
2. CLI Mode (Great for experienced users):
   python main.py --mode cli
   
   Features:
   - Command-line interface with rich formatting
   - Interactive assembly programming
   - Step-by-step debugging
   - Batch program execution
   - Scriptable operations

3. Test Mode (For developers):
   python main.py --mode test
   
   - Runs comprehensive test suite
   - Verifies all emulator components
   - Reports any issues found
   
4. Quick Test Mode:
   python main.py --mode quick
   
   - Runs basic functionality tests
   - Quick verification of core features

GETTING STARTED:

1. Try the GUI mode first:
   python main.py
   
2. Load a sample program:
   - In GUI: Use the "Programming" tab, select a sample program
   - In CLI: Type "samples" to list available programs
   
3. Learn with tutorials:
   - GUI: Check the example programs with built-in explanations
   - CLI: Use "help" command for detailed instruction reference

EXAMPLE PROGRAMS:

- hello_world: Basic I/O operations
- arithmetic: Addition and data processing  
- indirect: Demonstrates indirect addressing
- simple_loop: Loop programming with conditionals
- io_echo: Interactive I/O with devices

MICRO II QUICK REFERENCE:

Memory Reference Instructions:
  JMP addr    - Jump to address
  STR addr    - Store accumulator to memory
  ADD addr    - Add memory to accumulator
  
Register Instructions:  
  CLR         - Clear accumulator
  CMP         - Complement accumulator
  RTL/RTR     - Rotate accumulator left/right
  HLT         - Halt execution
  
I/O Instructions:
  INP dev     - Input from device
  OUT dev     - Output to device
  SFG dev     - Skip if device flag set

Skip Instructions:
  SNA         - Skip if accumulator non-zero
  SNO         - Skip if no overflow
  SZS         - Skip if sign bit zero

Assembly Directives:
  ORG addr    - Set assembly origin
  DATA value  - Define data word
  # comment   - Comment line

Use * for indirect addressing: ADD *15

TROUBLESHOOTING:

Problem: Import errors
Solution: Make sure all module files are in the same directory

Problem: GUI won't start  
Solution: Check that tkinter is installed (usually comes with Python)

Problem: Assembly errors
Solution: Check syntax - each instruction on separate line, proper operands

Problem: Program won't run
Solution: Make sure program ends with HLT instruction

For more help:
- GUI mode: Check the built-in help system
- CLI mode: Type "help" for command reference  
- Examples: Load sample programs to see working code

Happy programming with the MICRO II!
    """)

def run_gui_mode():
    """Start GUI mode"""
    try:
        from micro2_gui import MICRO2_GUI
        print("Starting MICRO II Emulator GUI...")
        print("Close the window to exit.")
        
        gui = MICRO2_GUI()
        gui.run()
        
    except ImportError as e:
        print(f"Failed to import GUI components: {e}")
        print("Make sure tkinter is installed.")
        return False
    except Exception as e:
        print(f"GUI Error: {e}")
        return False
    
    return True

def run_cli_mode():
    """Start CLI mode"""
    try:
        from micro2_cli import MICRO2_CLI
        print("Starting MICRO II Emulator CLI...")
        print("Type 'help' for commands, 'quit' to exit.\n")
        
        cli = MICRO2_CLI()
        cli.cmdloop()
        
    except ImportError as e:
        print(f"Failed to import CLI components: {e}")
        print("Try: pip install rich")
        return False
    except KeyboardInterrupt:
        print("\nGoodbye!")
        return True
    except Exception as e:
        print(f"CLI Error: {e}")
        return False
    
    return True

def run_test_mode():
    """Run test suite"""
    try:
        from micro2_tests import run_all_tests
        print("Running MICRO II Emulator Test Suite...")
        print("=" * 60)
        
        success = run_all_tests()
        
        if success:
            print("\n✓ All tests passed!")
            return True
        else:
            print("\n✗ Some tests failed!")
            return False
            
    except ImportError as e:
        print(f"Failed to import test components: {e}")
        return False
    except Exception as e:
        print(f"Test Error: {e}")
        return False

def run_quick_test():
    """Run quick functionality test"""
    try:
        from micro2_tests import run_quick_test
        run_quick_test()
        return True
        
    except ImportError as e:
        print(f"Failed to import test components: {e}")
        return False
    except Exception as e:
        print(f"Quick Test Error: {e}")
        return False

def create_example_programs():
    """Create example program files if they don't exist"""
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)
    
    # Simple hello world program
    hello_world = """# MICRO II Hello World Program
# Outputs "HI" to the console

CLR
ADD 10       # Load 'H' (72)
OUT 2        # Output to console
CLR  
ADD 11       # Load 'I' (73)
OUT 2        # Output to console
HLT

# Data section
ORG 10
DATA 72      # ASCII 'H'
DATA 73      # ASCII 'I'
"""
    
    # Write example file
    hello_file = examples_dir / "hello_world.asm"
    if not hello_file.exists():
        hello_file.write_text(hello_world)
    
    # Simple arithmetic program
    arithmetic = """# MICRO II Arithmetic Example  
# Calculates 15 + 27 = 42

CLR
ADD 10       # Add first number (15)
ADD 11       # Add second number (27)
STR 12       # Store result
OUT 4        # Display on LEDs
HLT

# Data section
ORG 10
DATA 15      # First number
DATA 27      # Second number  
DATA 0       # Result storage
"""
    
    arith_file = examples_dir / "arithmetic.asm"
    if not arith_file.exists():
        arith_file.write_text(arithmetic)
    
    return examples_dir

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MICRO II Computer Emulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start GUI mode (default)
  python main.py --mode cli         # Start command line mode
  python main.py --mode test        # Run test suite
  python main.py --mode help        # Show detailed help
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["gui", "cli", "test", "quick", "help"],
        default="gui",
        help="Emulator mode (default: gui)"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="MICRO II Emulator v1.0"
    )
    
    args = parser.parse_args()
    
    # Show help mode
    if args.mode == "help":
        show_help()
        return 0
    
    # Check dependencies for non-test modes
    if args.mode in ["gui", "cli"] and not check_dependencies():
        return 1
    
    # Create example programs
    try:
        examples_dir = create_example_programs()
        if args.mode == "gui":
            print(f"Example programs created in: {examples_dir.absolute()}")
    except Exception as e:
        print(f"Warning: Could not create example programs: {e}")
    
    # Run selected mode
    success = True
    
    if args.mode == "gui":
        success = run_gui_mode()
    elif args.mode == "cli":
        success = run_cli_mode()
    elif args.mode == "test":
        success = run_test_mode()
    elif args.mode == "quick":
        success = run_quick_test()
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
