"""
MICRO II Computer I/O System
Simulates peripheral devices and console I/O.
"""

import time
import threading
from queue import Queue, Empty

class MICRO2_IODevice:
    """Base class for I/O devices"""
    
    def __init__(self, device_id, name):
        self.device_id = device_id
        self.name = name
        self.flag = False
        self.enabled = True
    
    def input_data(self):
        """Return data for input instruction (8-bit)"""
        return 0
    
    def output_data(self, data):
        """Handle data from output instruction"""
        pass
    
    def set_flag(self, state):
        """Set device flag state"""
        self.flag = state
    
    def get_flag(self):
        """Get device flag state"""
        return self.flag
    
    def reset(self):
        """Reset device to initial state"""
        self.flag = False


class ConsoleInputDevice(MICRO2_IODevice):
    """Console input device"""
    
    def __init__(self, device_id=1):
        super().__init__(device_id, "Console Input")
        self.input_queue = Queue()
        self.input_thread = None
        self.running = False
    
    def start_input_thread(self):
        """Start background thread for input"""
        if not self.running:
            self.running = True
            self.input_thread = threading.Thread(target=self._input_worker, daemon=True)
            self.input_thread.start()
    
    def stop_input_thread(self):
        """Stop background input thread"""
        self.running = False
    
    def _input_worker(self):
        """Background worker for console input"""
        while self.running:
            try:
                # In a real implementation, this would handle console input
                # For now, we'll simulate with a simple mechanism
                time.sleep(0.1)
            except:
                break
    
    def queue_input(self, value):
        """Queue input value for the device"""
        if isinstance(value, str):
            # Convert string to ASCII values
            for char in value:
                self.input_queue.put(ord(char) & 0xFF)
        else:
            self.input_queue.put(value & 0xFF)
        self.set_flag(True)
    
    def input_data(self):
        """Get queued input data"""
        try:
            data = self.input_queue.get_nowait()
            if self.input_queue.empty():
                self.set_flag(False)
            return data
        except Empty:
            self.set_flag(False)
            return 0


class ConsoleOutputDevice(MICRO2_IODevice):
    """Console output device"""
    
    def __init__(self, device_id=2):
        super().__init__(device_id, "Console Output")
        self.output_buffer = []
        self.max_buffer_size = 1000
    
    def output_data(self, data):
        """Handle output data"""
        data = data & 0xFF
        
        # Store in buffer
        self.output_buffer.append(data)
        if len(self.output_buffer) > self.max_buffer_size:
            self.output_buffer.pop(0)
        
        # Convert to character if printable
        if 32 <= data <= 126:
            char = chr(data)
            print(f"Console Out: '{char}' ({data})")
        else:
            print(f"Console Out: {data} (0x{data:02X})")
    
    def get_output_text(self):
        """Get output as text string"""
        text = ""
        for data in self.output_buffer:
            if 32 <= data <= 126:
                text += chr(data)
            else:
                text += f"[{data}]"
        return text
    
    def clear_output(self):
        """Clear output buffer"""
        self.output_buffer.clear()


class DataSwitchDevice(MICRO2_IODevice):
    """Simulates data input switches"""
    
    def __init__(self, device_id=3):
        super().__init__(device_id, "Data Switches")
        self.switch_value = 0
        self.set_flag(True)  # Always ready
    
    def set_switches(self, value):
        """Set switch values"""
        self.switch_value = value & 0xFF
    
    def input_data(self):
        """Return current switch setting"""
        return self.switch_value


class LEDDisplayDevice(MICRO2_IODevice):
    """LED display output device"""
    
    def __init__(self, device_id=4):
        super().__init__(device_id, "LED Display")
        self.display_value = 0
    
    def output_data(self, data):
        """Display data on LEDs"""
        self.display_value = data & 0xFF
        print(f"LED Display: {self.display_value:08b} ({self.display_value})")
    
    def get_display_binary(self):
        """Get display value in binary format"""
        return f"{self.display_value:08b}"


class PaperTapeDevice(MICRO2_IODevice):
    """Simulates paper tape reader/punch"""
    
    def __init__(self, device_id=5):
        super().__init__(device_id, "Paper Tape")
        self.tape_data = []
        self.read_position = 0
        self.punch_data = []
    
    def load_tape(self, data):
        """Load data into tape reader"""
        if isinstance(data, str):
            self.tape_data = [ord(c) & 0xFF for c in data]
        else:
            self.tape_data = [d & 0xFF for d in data]
        self.read_position = 0
        self.set_flag(len(self.tape_data) > 0)
    
    def input_data(self):
        """Read next byte from tape"""
        if self.read_position < len(self.tape_data):
            data = self.tape_data[self.read_position]
            self.read_position += 1
            
            # Set flag based on remaining data
            self.set_flag(self.read_position < len(self.tape_data))
            return data
        else:
            self.set_flag(False)
            return 0
    
    def output_data(self, data):
        """Punch data to tape"""
        self.punch_data.append(data & 0xFF)
    
    def get_punched_data(self):
        """Get punched tape data"""
        return self.punch_data.copy()
    
    def clear_punch(self):
        """Clear punched data"""
        self.punch_data.clear()


class MICRO2_IOSystem:
    """I/O system managing all devices"""
    
    def __init__(self):
        self.devices = {}
        self.setup_default_devices()
    
    def setup_default_devices(self):
        """Setup default device configuration"""
        self.devices[0] = None  # Reserved for memory bank selection
        self.devices[1] = ConsoleInputDevice(1)
        self.devices[2] = ConsoleOutputDevice(2) 
        self.devices[3] = DataSwitchDevice(3)
        self.devices[4] = LEDDisplayDevice(4)
        self.devices[5] = PaperTapeDevice(5)
        self.devices[6] = None  # Available
        self.devices[7] = None  # Available
    
    def add_device(self, device_id, device):
        """Add a device to the system"""
        if 0 <= device_id <= 7:
            self.devices[device_id] = device
    
    def remove_device(self, device_id):
        """Remove a device from the system"""
        if device_id in self.devices:
            self.devices[device_id] = None
    
    def input_data(self, device_id):
        """Input data from specified device"""
        device = self.devices.get(device_id)
        if device and device.enabled:
            return device.input_data()
        return 0
    
    def output_data(self, device_id, data):
        """Output data to specified device"""
        device = self.devices.get(device_id)
        if device and device.enabled:
            device.output_data(data)
    
    def check_flag(self, device_id):
        """Check device flag status"""
        device = self.devices.get(device_id)
        if device and device.enabled:
            return device.get_flag()
        return False
    
    def reset_all_devices(self):
        """Reset all devices"""
        for device in self.devices.values():
            if device:
                device.reset()
    
    def get_device_status(self):
        """Get status of all devices"""
        status = {}
        for device_id, device in self.devices.items():
            if device:
                status[device_id] = {
                    'name': device.name,
                    'flag': device.get_flag(),
                    'enabled': device.enabled
                }
            else:
                status[device_id] = None
        return status
    
    # Convenience methods for specific devices
    def queue_console_input(self, text):
        """Queue text for console input device"""
        console_in = self.devices.get(1)
        if isinstance(console_in, ConsoleInputDevice):
            console_in.queue_input(text)
    
    def get_console_output(self):
        """Get console output text"""
        console_out = self.devices.get(2)
        if isinstance(console_out, ConsoleOutputDevice):
            return console_out.get_output_text()
        return ""
    
    def clear_console_output(self):
        """Clear console output"""
        console_out = self.devices.get(2)
        if isinstance(console_out, ConsoleOutputDevice):
            console_out.clear_output()
    
    def set_data_switches(self, value):
        """Set data switch device value"""
        switches = self.devices.get(3)
        if isinstance(switches, DataSwitchDevice):
            switches.set_switches(value)
    
    def load_paper_tape(self, data):
        """Load data into paper tape device"""
        tape = self.devices.get(5)
        if isinstance(tape, PaperTapeDevice):
            tape.load_tape(data)
    
    def get_paper_tape_output(self):
        """Get paper tape punched data"""
        tape = self.devices.get(5)
        if isinstance(tape, PaperTapeDevice):
            return tape.get_punched_data()
        return []


# Example I/O test programs
def create_io_test_programs():
    """Create test programs for I/O devices"""
    programs = {}
    
    programs['console_echo'] = """
        # Console echo program
        CLR
    LOOP:
        SFG 1        # Skip if console input ready
        JMP LOOP     # Wait for input
        INP 1        # Input character
        OUT 2        # Echo to output
        JMP LOOP     # Continue
    """
    
    programs['data_switches'] = """
        # Read data switches and display on LEDs
        CLR
        INP 3        # Input from data switches
        OUT 4        # Output to LED display
        HLT
    """
    
    programs['paper_tape_copy'] = """
        # Copy from paper tape to console
        CLR
    LOOP:
        SFG 5        # Skip if tape ready
        JMP END      # No more data
        INP 5        # Read from tape
        OUT 2        # Output to console
        JMP LOOP     # Continue
    END:
        HLT
    """
    
    return programs


if __name__ == "__main__":
    # Test I/O system
    io_system = MICRO2_IOSystem()
    
    print("MICRO II I/O System Test")
    print("Device Status:", io_system.get_device_status())
    
    # Test console I/O
    io_system.queue_console_input("Hello")
    print("Input ready:", io_system.check_flag(1))
    
    data = io_system.input_data(1)
    print(f"Input data: {data} ('{chr(data)}')")
    
    io_system.output_data(2, ord('H'))
    print("Console output:", io_system.get_console_output())
