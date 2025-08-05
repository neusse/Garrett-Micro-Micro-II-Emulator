"""
MICRO II Computer Command Line Interface
Provides a text-based interface for the emulator.
"""

import cmd
import sys
from micro2_emulator import MICRO2_Emulator
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm


class MICRO2_CLI(cmd.Cmd):
    """Command line interface for MICRO II emulator"""
    
    intro = """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                            MICRO II Computer Emulator                        ║
    ║                           Command Line Interface                             ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    
    Type 'help' or '?' to list commands.
    Type 'help <command>' for detailed help on a command.
    Type 'quit' or 'exit' to exit.
    """
    
    prompt = 'MICRO-II> '
    
    def __init__(self):
        super().__init__()
        self.console = Console()
        self.emulator = MICRO2_Emulator()
        self.current_program = ""
        
    def do_reset(self, arg):
        """Reset the emulator to initial state"""
        self.emulator.reset()
        self.console.print("[green]Emulator reset complete[/green]")
        self.show_status()
    
    def do_status(self, arg):
        """Show current system status"""
        self.show_status()
    
    def do_registers(self, arg):
        """Show CPU registers in detail"""
        state = self.emulator.cpu.get_state()
        registers = self.emulator.cpu.get_registers_binary()
        
        table = Table(title="CPU Registers")
        table.add_column("Register", style="cyan", no_wrap=True)
        table.add_column("Binary", style="green", no_wrap=True)
        table.add_column("Decimal", style="yellow", no_wrap=True)
        table.add_column("Hex", style="magenta", no_wrap=True)
        table.add_column("Notes", style="white")
        
        table.add_row("AC", registers['ac'], str(state['ac']), f"0x{state['ac']:02X}", 
                     "Accumulator")
        table.add_row("PC", registers['pc'], str(state['pc']), f"0x{state['pc']:02X}", 
                     "Program Counter")
        table.add_row("IR", registers['ir'], str(state['ir']), f"0x{state['ir']:02X}", 
                     "Instruction Register")
        
        # Disassemble current instruction
        if state['ir'] != 0:
            disasm = self.emulator.disassembler.disassemble_instruction(state['ir'])
            table.add_row("", "", "", "", f"Instruction: {disasm}")
        
        # Status flags
        flags = []
        if state['overflow']:
            flags.append("OVERFLOW")
        if state['running']:
            flags.append("RUNNING")
        if state['halted']:
            flags.append("HALTED")
        
        if flags:
            table.add_row("FLAGS", " ".join(flags), "", "", "Status Flags")
        
        self.console.print(table)
    
    def do_memory(self, arg):
        """Show memory contents. Usage: memory [page_num] or memory summary"""
        if not arg or arg.lower() == 'summary':
            content = self.emulator.get_memory_view()
        elif arg.isdigit():
            page_num = int(arg)
            if 0 <= page_num <= 7:
                content = self.emulator.get_memory_view(page_num)
            else:
                self.console.print("[red]Page number must be 0-7[/red]")
                return
        else:
            self.console.print("[red]Usage: memory [page_num] or memory summary[/red]")
            return
        
        self.console.print(Panel(content, title="Memory View"))
    
    def do_load(self, arg):
        """Load assembly program from file. Usage: load filename.asm"""
        if not arg:
            self.console.print("[red]Usage: load filename.asm[/red]")
            return
        
        try:
            with open(arg, 'r') as f:
                source_code = f.read()
            
            success, msg = self.emulator.load_assembly_program(source_code)
            if success:
                self.current_program = source_code
                self.console.print(f"[green]{msg}[/green]")
                self.show_status()
            else:
                self.console.print(f"[red]Load failed: {msg}[/red]")
                
        except FileNotFoundError:
            self.console.print(f"[red]File not found: {arg}[/red]")
        except Exception as e:
            self.console.print(f"[red]Error loading file: {e}[/red]")
    
    def do_assemble(self, arg):
        """Enter assembly code interactively"""
        self.console.print("Enter assembly code (type 'END' on a line by itself to finish):")
        lines = []
        
        while True:
            try:
                line = input("ASM> ")
                if line.strip().upper() == "END":
                    break
                lines.append(line)
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Assembly cancelled[/yellow]")
                return
        
        source_code = "\n".join(lines)
        success, msg = self.emulator.load_assembly_program(source_code)
        
        if success:
            self.current_program = source_code
            self.console.print(f"[green]{msg}[/green]")
            self.show_status()
        else:
            self.console.print(f"[red]Assembly failed: {msg}[/red]")
    
    def do_run(self, arg):
        """Run the loaded program"""
        if self.emulator.memory.read(0) == 0:
            self.console.print("[yellow]No program loaded. Use 'load' or 'assemble' first.[/yellow]")
            return
        
        self.emulator.cpu.pc = 0
        self.console.print("[blue]Running program...[/blue]")
        
        success, msg = self.emulator.run_program()
        
        if success:
            self.console.print(f"[green]Program completed: {msg}[/green]")
        else:
            self.console.print(f"[yellow]Program stopped: {msg}[/yellow]")
        
        self.show_status()
    
    def do_step(self, arg):
        """Execute single instruction. Usage: step [count]"""
        count = 1
        if arg and arg.isdigit():
            count = int(arg)
        
        for i in range(count):
            success, msg = self.emulator.single_step()
            if not success:
                self.console.print(f"[yellow]Step {i+1}: {msg}[/yellow]")
                break
            elif count == 1:
                # Show details for single step
                state = self.emulator.cpu.get_state()
                disasm = self.emulator.disassembler.disassemble_instruction(state['ir'])
                self.console.print(f"[cyan]Executed: {disasm}[/cyan]")
        
        self.show_status()
    
    def do_disassemble(self, arg):
        """Show disassembly of memory contents"""
        disassembly = self.emulator.disassemble_memory()
        syntax = Syntax(disassembly, "asm", theme="monokai", line_numbers=True)
        self.console.print(Panel(syntax, title="Program Disassembly"))
    
    def do_analyze(self, arg):
        """Analyze the current program"""
        analysis = self.emulator.analyze_program()
        self.console.print(Panel(analysis, title="Program Analysis"))
    
    def do_breakpoint(self, arg):
        """Set/clear breakpoints. Usage: breakpoint set <addr> | clear <addr> | list"""
        parts = arg.split()
        
        if not parts:
            self.console.print("[red]Usage: breakpoint set <addr> | clear <addr> | list[/red]")
            return
        
        command = parts[0].lower()
        
        if command == "set" and len(parts) == 2:
            try:
                addr = int(parts[1], 16) if parts[1].startswith('0x') else int(parts[1])
                self.emulator.set_breakpoint(addr)
                self.console.print(f"[green]Breakpoint set at address {addr:02X}[/green]")
            except ValueError:
                self.console.print("[red]Invalid address format[/red]")
        
        elif command == "clear" and len(parts) == 2:
            try:
                addr = int(parts[1], 16) if parts[1].startswith('0x') else int(parts[1])
                self.emulator.clear_breakpoint(addr)
                self.console.print(f"[green]Breakpoint cleared at address {addr:02X}[/green]")
            except ValueError:
                self.console.print("[red]Invalid address format[/red]")
        
        elif command == "list":
            breakpoints = self.emulator.get_breakpoints()
            if breakpoints:
                self.console.print("Active breakpoints:")
                for bp in breakpoints:
                    self.console.print(f"  {bp:02X}")
            else:
                self.console.print("No breakpoints set")
        
        else:
            self.console.print("[red]Usage: breakpoint set <addr> | clear <addr> | list[/red]")
    
    def do_switches(self, arg):
        """Set data switches. Usage: switches <8-bit value>"""
        if not arg:
            state = self.emulator.cpu.get_state()
            self.console.print(f"Data switches: {state['data_switches']:08b} ({state['data_switches']})")
            return
        
        try:
            if arg.startswith('0b'):
                value = int(arg, 2)
            elif arg.startswith('0x'):
                value = int(arg, 16)
            else:
                value = int(arg)
            
            if 0 <= value <= 255:
                self.emulator.set_data_switches(value)
                self.console.print(f"[green]Data switches set to: {value:08b} ({value})[/green]")
            else:
                self.console.print("[red]Value must be 0-255[/red]")
                
        except ValueError:
            self.console.print("[red]Invalid value format[/red]")
    
    def do_samples(self, arg):
        """List or load sample programs. Usage: samples [program_name]"""
        samples = self.emulator.get_sample_programs()
        
        if not arg:
            # List available samples
            table = Table(title="Available Sample Programs")
            table.add_column("Name", style="cyan")
            table.add_column("Description", style="white")
            
            descriptions = {
                'addition': 'Simple addition: 35 + 120',
                'indirect': 'Indirect addressing example',
                'counter': 'Simple counter loop',
                'io_test': 'I/O device test',
                'console_test': 'Console I/O test',
                'switch_test': 'Data switch test'
            }
            
            for name in samples.keys():
                desc = descriptions.get(name, "Sample program")
                table.add_row(name, desc)
            
            self.console.print(table)
            self.console.print("\nUse 'samples <name>' to load a program")
        
        elif arg in samples:
            # Load specific sample
            source_code = samples[arg]
            success, msg = self.emulator.load_assembly_program(source_code)
            
            if success:
                self.current_program = source_code
                self.console.print(f"[green]Sample '{arg}' loaded: {msg}[/green]")
                
                # Show the code
                syntax = Syntax(source_code, "asm", theme="monokai", line_numbers=True)
                self.console.print(Panel(syntax, title=f"Sample Program: {arg}"))
                
                self.show_status()
            else:
                self.console.print(f"[red]Failed to load sample: {msg}[/red]")
        
        else:
            self.console.print(f"[red]Unknown sample program: {arg}[/red]")
            self.console.print("Use 'samples' to list available programs")
    
    def do_io(self, arg):
        """Show I/O device status or send input. Usage: io [status] | io input <device> <data>"""
        if not arg or arg == "status":
            self.show_io_status()
        else:
            parts = arg.split()
            if len(parts) >= 3 and parts[0] == "input":
                try:
                    device_id = int(parts[1])
                    data = " ".join(parts[2:])  # Allow spaces in input
                    
                    if device_id == 1:  # Console input
                        self.emulator.io_system.queue_console_input(data)
                        self.console.print(f"[green]Queued input to device {device_id}: '{data}'[/green]")
                    else:
                        # Convert to numeric value
                        if data.startswith('0x'):
                            value = int(data, 16)
                        elif data.startswith('0b'):
                            value = int(data, 2)
                        else:
                            value = int(data)
                        
                        # Simulate input (this would need device-specific handling)
                        self.console.print(f"[yellow]Input simulation not implemented for device {device_id}[/yellow]")
                        
                except ValueError:
                    self.console.print("[red]Invalid device ID or data format[/red]")
            else:
                self.console.print("[red]Usage: io [status] | io input <device> <data>[/red]")
    
    def do_save(self, arg):
        """Save current program to file. Usage: save filename.asm"""
        if not arg:
            self.console.print("[red]Usage: save filename.asm[/red]")
            return
        
        if not self.current_program:
            self.console.print("[yellow]No program to save[/yellow]")
            return
        
        try:
            with open(arg, 'w') as f:
                f.write(self.current_program)
            self.console.print(f"[green]Program saved to {arg}[/green]")
        except Exception as e:
            self.console.print(f"[red]Error saving file: {e}[/red]")
    
    def do_debug(self, arg):
        """Enable/disable debug mode. Usage: debug [on|off]"""
        if not arg:
            state = self.emulator.get_system_state()
            status = "enabled" if state['debug_mode'] else "disabled"
            self.console.print(f"Debug mode is {status}")
        elif arg.lower() in ['on', 'enable', 'true']:
            self.emulator.enable_debug_mode(True)
            self.console.print("[green]Debug mode enabled[/green]")
        elif arg.lower() in ['off', 'disable', 'false']:
            self.emulator.enable_debug_mode(False)
            self.console.print("[green]Debug mode disabled[/green]")
        else:
            self.console.print("[red]Usage: debug [on|off][/red]")
    
    def do_help(self, arg):
        """Show help for commands"""
        if arg:
            # Show detailed help for specific command
            super().do_help(arg)
        else:
            # Show command summary
            self.console.print(Panel("""
Available commands:

[cyan]System Control:[/cyan]
  reset          - Reset emulator to initial state
  status         - Show system status
  registers      - Show CPU registers in detail
  memory [page]  - Show memory contents
  debug [on|off] - Enable/disable debug mode

[cyan]Programming:[/cyan]
  load <file>    - Load assembly program from file
  assemble       - Enter assembly code interactively
  save <file>    - Save current program to file
  samples [name] - List or load sample programs

[cyan]Execution:[/cyan]
  run            - Run the loaded program
  step [count]   - Execute single instruction(s)
  breakpoint     - Set/clear/list breakpoints

[cyan]Analysis:[/cyan]
  disassemble    - Show program disassembly
  analyze        - Analyze current program

[cyan]I/O & Hardware:[/cyan]
  switches <val> - Set data switches value
  io [status]    - Show I/O device status
  io input       - Send input to device

[cyan]Other:[/cyan]
  help [cmd]     - Show help
  quit/exit      - Exit emulator
            """, title="MICRO II Emulator Commands"))
    
    def do_quit(self, arg):
        """Exit the emulator"""
        if Confirm.ask("Are you sure you want to exit?"):
            self.console.print("[yellow]Goodbye![/yellow]")
            return True
    
    def do_exit(self, arg):
        """Exit the emulator"""
        return self.do_quit(arg)
    
    def do_EOF(self, arg):
        """Handle Ctrl+D"""
        self.console.print()
        return self.do_quit(arg)
    
    def show_status(self):
        """Display current system status"""
        state = self.emulator.cpu.get_state()
        memory_info = self.emulator.memory.get_memory_info()
        
        # Create status table
        table = Table(title="System Status")
        table.add_column("Component", style="cyan", no_wrap=True)
        table.add_column("Status", style="green")
        
        # CPU status
        cpu_status = []
        if state['running']:
            cpu_status.append("RUNNING")
        if state['halted']:
            cpu_status.append("HALTED")
        if state['overflow']:
            cpu_status.append("OVERFLOW")
        
        table.add_row("CPU", " | ".join(cpu_status) if cpu_status else "READY")
        table.add_row("PC", f"{state['pc']:02X} ({state['pc']})")
        table.add_row("AC", f"{state['ac']:02X} ({state['ac']})")
        table.add_row("Memory Bank", f"{memory_info['current_bank']}/{memory_info['num_banks']}")
        table.add_row("Data Switches", f"{state['data_switches']:08b} ({state['data_switches']})")
        
        self.console.print(table)
    
    def show_io_status(self):
        """Show I/O device status"""
        status = self.emulator.io_system.get_device_status()
        
        table = Table(title="I/O Device Status")
        table.add_column("Device", style="cyan", no_wrap=True)
        table.add_column("Name", style="white")
        table.add_column("Flag", style="yellow")
        table.add_column("Status", style="green")
        
        for device_id, info in status.items():
            if info:
                flag_status = "SET" if info['flag'] else "CLEAR"
                enabled_status = "ENABLED" if info['enabled'] else "DISABLED"
                table.add_row(str(device_id), info['name'], flag_status, enabled_status)
            else:
                table.add_row(str(device_id), "Not installed", "-", "-")
        
        self.console.print(table)
        
        # Show console output if any
        console_output = self.emulator.io_system.get_console_output()
        if console_output:
            self.console.print(Panel(console_output, title="Console Output"))
    
    def onecmd(self, line):
        """Override to handle empty lines gracefully"""
        if not line.strip():
            return False
        return super().onecmd(line)
    
    def emptyline(self):
        """Do nothing on empty line"""
        pass


def main():
    """Main entry point for CLI"""
    try:
        cli = MICRO2_CLI()
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
