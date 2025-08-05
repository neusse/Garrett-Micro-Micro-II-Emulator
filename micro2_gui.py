"""
MICRO II Computer GUI Interface
Provides a graphical front panel and programming interface.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
from micro2_emulator import MICRO2_Emulator


class MICRO2_GUI:
    def __init__(self):
        self.emulator = MICRO2_Emulator()
        self.running_program = False
        self.update_thread = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("MICRO II Computer Emulator")
        self.root.geometry("1200x800")
        
        # Setup GUI
        self.setup_gui()
        self.update_displays()
        
        # Start periodic updates
        self.start_update_timer()
    
    def setup_gui(self):
        """Setup the main GUI layout"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_front_panel_tab()
        self.create_programming_tab()
        self.create_memory_tab()
        self.create_io_tab()
        self.create_debug_tab()
    
    def create_front_panel_tab(self):
        """Create front panel simulation tab"""
        self.front_panel_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.front_panel_frame, text="Front Panel")
        
        # Title
        title_label = tk.Label(self.front_panel_frame, text="MICRO II COMPUTER", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # LED displays frame
        displays_frame = tk.LabelFrame(self.front_panel_frame, text="Register Displays", 
                                     font=("Arial", 12, "bold"))
        displays_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # AC display
        ac_frame = tk.Frame(displays_frame)
        ac_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(ac_frame, text="AC:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.ac_display = tk.Label(ac_frame, text="00000000", font=("Courier", 12), 
                                  bg="black", fg="red")
        self.ac_display.pack(side=tk.LEFT, padx=10)
        self.ac_decimal = tk.Label(ac_frame, text="(0)", font=("Arial", 10))
        self.ac_decimal.pack(side=tk.LEFT, padx=5)
        
        # PC display
        pc_frame = tk.Frame(displays_frame)
        pc_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(pc_frame, text="PC:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.pc_display = tk.Label(pc_frame, text="00000000", font=("Courier", 12), 
                                  bg="black", fg="red")
        self.pc_display.pack(side=tk.LEFT, padx=10)
        self.pc_decimal = tk.Label(pc_frame, text="(0)", font=("Arial", 10))
        self.pc_decimal.pack(side=tk.LEFT, padx=5)
        
        # IR display
        ir_frame = tk.Frame(displays_frame)
        ir_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(ir_frame, text="IR:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.ir_display = tk.Label(ir_frame, text="00000000", font=("Courier", 12), 
                                  bg="black", fg="red")
        self.ir_display.pack(side=tk.LEFT, padx=10)
        self.ir_decimal = tk.Label(ir_frame, text="(0)", font=("Arial", 10))
        self.ir_decimal.pack(side=tk.LEFT, padx=5)
        self.ir_disasm = tk.Label(ir_frame, text="NOP", font=("Arial", 10))
        self.ir_disasm.pack(side=tk.LEFT, padx=10)
        
        # Status lights
        status_frame = tk.Frame(displays_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.run_light = tk.Label(status_frame, text="RUN", font=("Arial", 10, "bold"),
                                 bg="gray", fg="white", width=6)
        self.run_light.pack(side=tk.LEFT, padx=5)
        
        self.overflow_light = tk.Label(status_frame, text="OVRFL", font=("Arial", 10, "bold"),
                                      bg="gray", fg="white", width=6)
        self.overflow_light.pack(side=tk.LEFT, padx=5)
        
        self.halt_light = tk.Label(status_frame, text="HALT", font=("Arial", 10, "bold"),
                                  bg="gray", fg="white", width=6)
        self.halt_light.pack(side=tk.LEFT, padx=5)
        
        # Data switches
        switches_frame = tk.LabelFrame(self.front_panel_frame, text="Data Switches", 
                                     font=("Arial", 12, "bold"))
        switches_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.switch_vars = []
        switch_bits_frame = tk.Frame(switches_frame)
        switch_bits_frame.pack(pady=5)
        
        for i in range(8):
            bit_frame = tk.Frame(switch_bits_frame)
            bit_frame.pack(side=tk.LEFT, padx=2)
            
            tk.Label(bit_frame, text=str(7-i), font=("Arial", 8)).pack()
            
            var = tk.BooleanVar()
            self.switch_vars.append(var)
            cb = tk.Checkbutton(bit_frame, variable=var, command=self.update_data_switches)
            cb.pack()
        
        # Switch value display
        self.switch_value_label = tk.Label(switches_frame, text="Value: 00000000 (0)", 
                                          font=("Arial", 10))
        self.switch_value_label.pack(pady=2)
        
        # Control buttons
        controls_frame = tk.LabelFrame(self.front_panel_frame, text="Controls", 
                                     font=("Arial", 12, "bold"))
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # RUN/STOP switch
        switch_frame = tk.Frame(controls_frame)
        switch_frame.pack(side=tk.LEFT, padx=10, pady=5)
        tk.Label(switch_frame, text="RUN/STOP", font=("Arial", 10, "bold")).pack()
        self.run_stop_var = tk.BooleanVar()
        self.run_stop_switch = tk.Checkbutton(switch_frame, text="RUN", 
                                            variable=self.run_stop_var,
                                            command=self.toggle_run_stop)
        self.run_stop_switch.pack()
        
        # Control buttons
        buttons_frame = tk.Frame(controls_frame)
        buttons_frame.pack(side=tk.LEFT, padx=20, pady=5)
        
        tk.Button(buttons_frame, text="LOAD ADDR", command=self.load_address,
                 font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(buttons_frame, text="LOAD DATA", command=self.load_data,
                 font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(buttons_frame, text="DISPLAY", command=self.display_memory,
                 font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(buttons_frame, text="START/STEP", command=self.start_step,
                 font=("Arial", 9), bg="lightgreen").pack(side=tk.LEFT, padx=2)
        tk.Button(buttons_frame, text="RESET", command=self.reset_emulator,
                 font=("Arial", 9), bg="lightcoral").pack(side=tk.LEFT, padx=2)
    
    def create_programming_tab(self):
        """Create programming interface tab"""
        self.programming_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.programming_frame, text="Programming")
        
        # Split into left (editor) and right (output)
        paned = tk.PanedWindow(self.programming_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side - editor
        editor_frame = tk.LabelFrame(paned, text="Assembly Editor", font=("Arial", 12, "bold"))
        paned.add(editor_frame, width=600)
        
        # Editor toolbar
        editor_toolbar = tk.Frame(editor_frame)
        editor_toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Button(editor_toolbar, text="Load", command=self.load_program_file).pack(side=tk.LEFT, padx=2)
        tk.Button(editor_toolbar, text="Save", command=self.save_program_file).pack(side=tk.LEFT, padx=2)
        tk.Button(editor_toolbar, text="Assemble", command=self.assemble_program, 
                 bg="lightblue").pack(side=tk.LEFT, padx=2)
        tk.Button(editor_toolbar, text="Run", command=self.run_program, 
                 bg="lightgreen").pack(side=tk.LEFT, padx=2)
        
        # Sample programs dropdown
        tk.Label(editor_toolbar, text="Samples:").pack(side=tk.LEFT, padx=(10,2))
        self.sample_var = tk.StringVar()
        sample_combo = ttk.Combobox(editor_toolbar, textvariable=self.sample_var, 
                                   values=list(self.emulator.get_sample_programs().keys()),
                                   state="readonly", width=15)
        sample_combo.pack(side=tk.LEFT, padx=2)
        sample_combo.bind("<<ComboboxSelected>>", self.load_sample_program)
        
        # Text editor
        self.code_editor = scrolledtext.ScrolledText(editor_frame, height=25, 
                                                    font=("Courier", 10))
        self.code_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right side - output and disassembly
        output_frame = tk.LabelFrame(paned, text="Output", font=("Arial", 12, "bold"))
        paned.add(output_frame, width=400)
        
        # Output notebook
        output_notebook = ttk.Notebook(output_frame)
        output_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Assembly output
        asm_output_frame = ttk.Frame(output_notebook)
        output_notebook.add(asm_output_frame, text="Assembly")
        self.assembly_output = scrolledtext.ScrolledText(asm_output_frame, height=15, 
                                                        font=("Courier", 9))
        self.assembly_output.pack(fill=tk.BOTH, expand=True)
        
        # Disassembly
        disasm_frame = ttk.Frame(output_notebook)
        output_notebook.add(disasm_frame, text="Disassembly")
        self.disasm_output = scrolledtext.ScrolledText(disasm_frame, height=15, 
                                                      font=("Courier", 9))
        self.disasm_output.pack(fill=tk.BOTH, expand=True)
    
    def create_memory_tab(self):
        """Create memory view tab"""
        self.memory_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.memory_frame, text="Memory")
        
        # Memory controls
        controls_frame = tk.Frame(self.memory_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(controls_frame, text="Refresh", command=self.update_memory_view).pack(side=tk.LEFT, padx=2)
        tk.Button(controls_frame, text="Clear Memory", command=self.clear_memory).pack(side=tk.LEFT, padx=2)
        
        tk.Label(controls_frame, text="View:").pack(side=tk.LEFT, padx=(10,2))
        self.memory_view_var = tk.StringVar(value="Summary")
        view_combo = ttk.Combobox(controls_frame, textvariable=self.memory_view_var,
                                 values=["Summary"] + [f"Page {i}" for i in range(8)],
                                 state="readonly")
        view_combo.pack(side=tk.LEFT, padx=2)
        view_combo.bind("<<ComboboxSelected>>", self.change_memory_view)
        
        # Memory display
        self.memory_display = scrolledtext.ScrolledText(self.memory_frame, height=30, 
                                                       font=("Courier", 9))
        self.memory_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_io_tab(self):
        """Create I/O devices tab"""
        self.io_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.io_frame, text="I/O Devices")
        
        # Device status
        status_frame = tk.LabelFrame(self.io_frame, text="Device Status", 
                                   font=("Arial", 12, "bold"))
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.device_status_text = tk.Text(status_frame, height=8, font=("Courier", 9))
        self.device_status_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Console I/O
        console_frame = tk.LabelFrame(self.io_frame, text="Console I/O", 
                                    font=("Arial", 12, "bold"))
        console_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Console input
        input_frame = tk.Frame(console_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(input_frame, text="Input:").pack(side=tk.LEFT)
        self.console_input_entry = tk.Entry(input_frame, width=30)
        self.console_input_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(input_frame, text="Send", command=self.send_console_input).pack(side=tk.LEFT, padx=2)
        self.console_input_entry.bind("<Return>", lambda e: self.send_console_input())
        
        # Console output
        tk.Label(console_frame, text="Output:", anchor="w").pack(fill=tk.X, padx=5)
        self.console_output = scrolledtext.ScrolledText(console_frame, height=10, 
                                                       font=("Courier", 9))
        self.console_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # Console controls
        console_controls = tk.Frame(console_frame)
        console_controls.pack(fill=tk.X, padx=5, pady=2)
        tk.Button(console_controls, text="Clear Output", 
                 command=self.clear_console_output).pack(side=tk.LEFT, padx=2)
    
    def create_debug_tab(self):
        """Create debugging tab"""
        self.debug_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.debug_frame, text="Debug")
        
        # Debug controls
        debug_controls = tk.LabelFrame(self.debug_frame, text="Debug Controls", 
                                     font=("Arial", 12, "bold"))
        debug_controls.pack(fill=tk.X, padx=5, pady=5)
        
        controls_row1 = tk.Frame(debug_controls)
        controls_row1.pack(fill=tk.X, padx=5, pady=2)
        
        self.debug_mode_var = tk.BooleanVar()
        tk.Checkbutton(controls_row1, text="Debug Mode", variable=self.debug_mode_var,
                      command=self.toggle_debug_mode).pack(side=tk.LEFT, padx=5)
        
        tk.Button(controls_row1, text="Single Step", command=self.debug_single_step).pack(side=tk.LEFT, padx=2)
        tk.Button(controls_row1, text="Continue", command=self.debug_continue).pack(side=tk.LEFT, padx=2)
        
        # Breakpoints
        bp_frame = tk.Frame(debug_controls)
        bp_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(bp_frame, text="Breakpoint:").pack(side=tk.LEFT)
        self.breakpoint_entry = tk.Entry(bp_frame, width=10)
        self.breakpoint_entry.pack(side=tk.LEFT, padx=2)
        tk.Button(bp_frame, text="Set", command=self.set_breakpoint).pack(side=tk.LEFT, padx=2)
        tk.Button(bp_frame, text="Clear All", command=self.clear_breakpoints).pack(side=tk.LEFT, padx=2)
        
        # Analysis output
        analysis_frame = tk.LabelFrame(self.debug_frame, text="Program Analysis", 
                                     font=("Arial", 12, "bold"))
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        analysis_controls = tk.Frame(analysis_frame)
        analysis_controls.pack(fill=tk.X, padx=5, pady=2)
        tk.Button(analysis_controls, text="Analyze Program", 
                 command=self.analyze_program).pack(side=tk.LEFT, padx=2)
        tk.Button(analysis_controls, text="Show Disassembly", 
                 command=self.show_disassembly).pack(side=tk.LEFT, padx=2)
        
        self.analysis_output = scrolledtext.ScrolledText(analysis_frame, height=20, 
                                                        font=("Courier", 9))
        self.analysis_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Event handlers
    def update_data_switches(self):
        """Update data switches value"""
        value = 0
        for i, var in enumerate(self.switch_vars):
            if var.get():
                value |= (1 << (7-i))
        
        self.emulator.set_data_switches(value)
        self.switch_value_label.config(text=f"Value: {value:08b} ({value})")
    
    def toggle_run_stop(self):
        """Toggle RUN/STOP switch"""
        run_mode = self.run_stop_var.get()
        self.emulator.set_run_stop_switch(run_mode)
        self.run_stop_switch.config(text="RUN" if run_mode else "STOP")
    
    def load_address(self):
        """Load address from data switches"""
        self.emulator.press_load_address()
        self.update_displays()
    
    def load_data(self):
        """Load data from data switches"""
        self.emulator.press_load_data()
        self.update_displays()
    
    def display_memory(self):
        """Display memory at PC address"""
        self.emulator.press_display()
        self.update_displays()
    
    def start_step(self):
        """Start/step execution"""
        if self.run_stop_var.get():
            # RUN mode - start continuous execution
            self.start_continuous_execution()
        else:
            # STOP mode - single step
            success, msg = self.emulator.single_step()
            if not success:
                messagebox.showinfo("Execution", msg)
            self.update_displays()
    
    def start_continuous_execution(self):
        """Start continuous execution in separate thread"""
        if not self.running_program:
            self.running_program = True
            thread = threading.Thread(target=self.run_program_thread, daemon=True)
            thread.start()
    
    def run_program_thread(self):
        """Run program in separate thread"""
        try:
            success, msg = self.emulator.run_program()
            self.running_program = False
            
            # Update GUI in main thread
            self.root.after(0, lambda: self.show_execution_result(success, msg))
        except Exception as e:
            self.running_program = False
            self.root.after(0, lambda: messagebox.showerror("Execution Error", str(e)))
    
    def show_execution_result(self, success, msg):
        """Show execution result"""
        self.update_displays()
        if not success:
            messagebox.showinfo("Execution Complete", msg)
    
    def reset_emulator(self):
        """Reset the emulator"""
        self.emulator.reset()
        self.running_program = False
        
        # Reset GUI controls
        for var in self.switch_vars:
            var.set(False)
        self.run_stop_var.set(False)
        self.run_stop_switch.config(text="STOP")
        
        self.update_displays()
        self.update_memory_view()
        messagebox.showinfo("Reset", "Emulator reset complete")
    
    # Programming tab methods
    def load_program_file(self):
        """Load program from file"""
        filename = filedialog.askopenfilename(
            title="Load Program",
            filetypes=[("Assembly files", "*.asm"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                self.code_editor.delete(1.0, tk.END)
                self.code_editor.insert(1.0, content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
    
    def save_program_file(self):
        """Save program to file"""
        filename = filedialog.asksaveasfilename(
            title="Save Program",
            defaultextension=".asm",
            filetypes=[("Assembly files", "*.asm"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                content = self.code_editor.get(1.0, tk.END)
                with open(filename, 'w') as f:
                    f.write(content)
                messagebox.showinfo("Saved", f"Program saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
    
    def load_sample_program(self, event=None):
        """Load selected sample program"""
        sample_name = self.sample_var.get()
        if sample_name:
            samples = self.emulator.get_sample_programs()
            if sample_name in samples:
                self.code_editor.delete(1.0, tk.END)
                self.code_editor.insert(1.0, samples[sample_name])
    
    def assemble_program(self):
        """Assemble the current program"""
        source_code = self.code_editor.get(1.0, tk.END)
        success, msg = self.emulator.load_assembly_program(source_code)
        
        self.assembly_output.delete(1.0, tk.END)
        if success:
            self.assembly_output.insert(tk.END, f"Assembly successful: {msg}\n\n")
            # Show machine code
            machine_code = []
            for addr in range(256):
                data = self.emulator.memory.read(addr)
                if data != 0:
                    machine_code.append((addr, data))
            
            self.assembly_output.insert(tk.END, "Machine Code:\n")
            self.assembly_output.insert(tk.END, "Addr Binary   Hex Dec\n")
            self.assembly_output.insert(tk.END, "-" * 20 + "\n")
            
            for addr, data in machine_code:
                self.assembly_output.insert(tk.END, f"{addr:02X}: {data:08b} {data:02X}  {data:3d}\n")
        else:
            self.assembly_output.insert(tk.END, f"Assembly failed:\n{msg}")
        
        self.update_displays()
        self.update_memory_view()
    
    def run_program(self):
        """Run the assembled program"""
        if self.emulator.memory.read(0) == 0:
            messagebox.showwarning("No Program", "Please assemble a program first")
            return
        
        self.emulator.cpu.pc = 0
        success, msg = self.emulator.run_program()
        
        self.update_displays()
        messagebox.showinfo("Execution Complete", msg)
    
    # Memory tab methods
    def update_memory_view(self):
        """Update memory display"""
        view = self.memory_view_var.get()
        
        self.memory_display.delete(1.0, tk.END)
        
        if view == "Summary":
            content = self.emulator.get_memory_view()
        else:
            page_num = int(view.split()[1])
            content = self.emulator.get_memory_view(page_num)
        
        self.memory_display.insert(1.0, content)
    
    def change_memory_view(self, event=None):
        """Change memory view"""
        self.update_memory_view()
    
    def clear_memory(self):
        """Clear all memory"""
        self.emulator.memory.clear_memory()
        self.update_memory_view()
        self.update_displays()
        messagebox.showinfo("Memory", "Memory cleared")
    
    # I/O tab methods
    def send_console_input(self):
        """Send console input"""
        text = self.console_input_entry.get()
        if text:
            self.emulator.io_system.queue_console_input(text)
            self.console_input_entry.delete(0, tk.END)
            self.update_device_status()
    
    def clear_console_output(self):
        """Clear console output"""
        self.console_output.delete(1.0, tk.END)
        self.emulator.io_system.clear_console_output()
    
    def update_device_status(self):
        """Update device status display"""
        status = self.emulator.io_system.get_device_status()
        
        self.device_status_text.delete(1.0, tk.END)
        self.device_status_text.insert(tk.END, "Device Status:\n")
        self.device_status_text.insert(tk.END, "-" * 30 + "\n")
        
        for device_id, info in status.items():
            if info:
                flag_status = "SET" if info['flag'] else "CLEAR"
                enabled_status = "ON" if info['enabled'] else "OFF"
                self.device_status_text.insert(tk.END, 
                    f"Device {device_id}: {info['name']}\n")
                self.device_status_text.insert(tk.END, 
                    f"  Flag: {flag_status}, Status: {enabled_status}\n")
        
        # Update console output
        output_text = self.emulator.io_system.get_console_output()
        if output_text:
            current_text = self.console_output.get(1.0, tk.END)
            if output_text not in current_text:
                self.console_output.insert(tk.END, output_text)
                self.console_output.see(tk.END)
    
    # Debug tab methods
    def toggle_debug_mode(self):
        """Toggle debug mode"""
        debug_mode = self.debug_mode_var.get()
        self.emulator.enable_debug_mode(debug_mode)
    
    def debug_single_step(self):
        """Debug single step"""
        success, msg = self.emulator.single_step()
        if not success:
            messagebox.showinfo("Debug", msg)
        self.update_displays()
        self.update_debug_info()
    
    def debug_continue(self):
        """Continue execution"""
        self.start_continuous_execution()
    
    def set_breakpoint(self):
        """Set breakpoint"""
        try:
            addr_str = self.breakpoint_entry.get()
            if addr_str.startswith('0x') or addr_str.startswith('0X'):
                addr = int(addr_str, 16)
            else:
                addr = int(addr_str)
            
            self.emulator.set_breakpoint(addr)
            self.breakpoint_entry.delete(0, tk.END)
            self.update_debug_info()
            messagebox.showinfo("Breakpoint", f"Breakpoint set at address {addr:02X}")
        except ValueError:
            messagebox.showerror("Error", "Invalid address format")
    
    def clear_breakpoints(self):
        """Clear all breakpoints"""
        self.emulator.clear_all_breakpoints()
        self.update_debug_info()
        messagebox.showinfo("Breakpoints", "All breakpoints cleared")
    
    def analyze_program(self):
        """Analyze current program"""
        analysis = self.emulator.analyze_program()
        self.analysis_output.delete(1.0, tk.END)
        self.analysis_output.insert(1.0, analysis)
    
    def show_disassembly(self):
        """Show program disassembly"""
        disassembly = self.emulator.disassemble_memory()
        self.disasm_output.delete(1.0, tk.END)
        self.disasm_output.insert(1.0, disassembly)
    
    def update_debug_info(self):
        """Update debug information"""
        breakpoints = self.emulator.get_breakpoints()
        bp_text = ", ".join([f"{bp:02X}" for bp in breakpoints]) if breakpoints else "None"
        
        # Could add more debug info here
        pass
    
    # Display update methods
    def update_displays(self):
        """Update all LED displays"""
        registers = self.emulator.cpu.get_registers_binary()
        state = self.emulator.cpu.get_state()
        
        # Update register displays
        self.ac_display.config(text=registers['ac'])
        self.ac_decimal.config(text=f"({state['ac']})")
        
        self.pc_display.config(text=registers['pc'])
        self.pc_decimal.config(text=f"({state['pc']})")
        
        self.ir_display.config(text=registers['ir'])
        self.ir_decimal.config(text=f"({state['ir']})")
        
        # Disassemble current instruction
        if state['ir'] != 0:
            disasm = self.emulator.disassembler.disassemble_instruction(state['ir'])
            self.ir_disasm.config(text=disasm)
        else:
            self.ir_disasm.config(text="")
        
        # Update status lights
        self.run_light.config(bg="green" if state['running'] else "gray")
        self.overflow_light.config(bg="red" if state['overflow'] else "gray")
        self.halt_light.config(bg="red" if state['halted'] else "gray")
    
    def start_update_timer(self):
        """Start periodic display updates"""
        self.update_displays()
        self.update_device_status()
        self.root.after(100, self.start_update_timer)  # Update every 100ms
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    gui = MICRO2_GUI()
    gui.run()
