"""
MICRO II Computer Example Programs and Tutorials
Educational programs to demonstrate various features and concepts.
"""

class MICRO2_Examples:
    """Collection of example programs and tutorials"""
    
    def __init__(self):
        self.examples = {}
        self.tutorials = {}
        self.setup_examples()
        self.setup_tutorials()
    
    def setup_examples(self):
        """Setup example programs"""
        
        # Basic arithmetic
        self.examples['hello_world'] = {
            'name': 'Hello World',
            'description': 'Basic program that outputs ASCII "HELLO" to console',
            'difficulty': 'Beginner',
            'code': '''
# Hello World - Output "HELLO" to console
CLR
ADD 20      # Load 'H' (72)
OUT 2       # Output to console
CLR
ADD 21      # Load 'E' (69) 
OUT 2       # Output to console
CLR
ADD 22      # Load 'L' (76)
OUT 2       # Output to console
OUT 2       # Output 'L' again
CLR
ADD 23      # Load 'O' (79)
OUT 2       # Output to console
HLT

# ASCII data
ORG 20
DATA 72     # 'H'
DATA 69     # 'E'
DATA 76     # 'L'
DATA 79     # 'O'
            ''',
            'expected_output': 'HELLO on console device',
            'concepts': ['Basic instructions', 'Memory addressing', 'I/O operations']
        }
        
        self.examples['arithmetic'] = {
            'name': 'Arithmetic Operations',
            'description': 'Demonstrates addition and complement operations',
            'difficulty': 'Beginner',
            'code': '''
# Arithmetic Example: Calculate (A + B) - C
CLR          # Clear accumulator
ADD 20       # Add A (value 15)
ADD 21       # Add B (value 27) 
STR 24       # Store A + B = 42
ADD 22       # Add C (value 8)
CMP          # Complement (two's complement would need additional step)
ADD 25       # Add 1 to complete two's complement
ADD 24       # Add back (A + B) to get (A + B) - C
STR 23       # Store result
HLT

# Data section
ORG 20
DATA 15      # A
DATA 27      # B  
DATA 8       # C
DATA 0       # Result storage
DATA 0       # Temp storage for A+B
DATA 1       # Constant 1
            ''',
            'expected_output': 'Result should be 34 at address 23',
            'concepts': ['Addition', 'Complement', 'Memory operations']
        }
        
        self.examples['indirect_addressing'] = {
            'name': 'Indirect Addressing',
            'description': 'Shows how to use indirect addressing for flexible memory access',
            'difficulty': 'Intermediate',
            'code': '''
# Indirect Addressing Example
# Copy data from one location to another using pointers

CLR
ADD *16      # Add value pointed to by address 16
STR *17      # Store to location pointed to by address 17
ADD *18      # Add another indirect value
STR *19      # Store to another indirect location
HLT

# Pointer table (addresses 16-19)
ORG 16
DATA 128     # Points to address 128
DATA 129     # Points to address 129  
DATA 130     # Points to address 130
DATA 131     # Points to address 131

# Data section (addresses 128-131)
ORG 128
DATA 42      # Source data 1
DATA 0       # Destination 1
DATA 99      # Source data 2
DATA 0       # Destination 2
            ''',
            'expected_output': 'Data copied via indirect addressing',
            'concepts': ['Indirect addressing', 'Pointers', 'Memory management']
        }
        
        self.examples['simple_loop'] = {
            'name': 'Simple Loop',
            'description': 'Counting loop using conditional jumps',
            'difficulty': 'Intermediate', 
            'code': '''
# Simple counting loop - count from 1 to 5
CLR          # Clear counter
STR 20       # Store initial count (0)

LOOP:
ADD 21       # Add 1 to counter
STR 20       # Update counter
STR 22       # Also store for comparison
ADD 23       # Add -5 (to check if we've reached 5)
SNA          # Skip if result is non-zero (not reached 5)
JMP END      # If zero, we've counted to 5, exit
CLR          # Clear for next iteration  
JMP LOOP     # Continue loop

END:
CLR
ADD 20       # Load final count
OUT 4        # Display on LEDs
HLT

# Data section
ORG 20
DATA 0       # Counter storage
DATA 1       # Increment value
DATA 0       # Temp storage
DATA 251     # -5 in two's complement (256-5)
            ''',
            'expected_output': 'Final count of 5 displayed on LEDs',
            'concepts': ['Loops', 'Conditional jumps', 'Counters']
        }
        
        self.examples['io_echo'] = {
            'name': 'I/O Echo Program',
            'description': 'Reads from input device and echoes to output',
            'difficulty': 'Intermediate',
            'code': '''
# I/O Echo Program
# Continuously read from console input and echo to output

MAIN_LOOP:
    SFG 1        # Skip if input device flag set
    JMP MAIN_LOOP # Wait for input
    
    INP 1        # Input character from device 1
    OUT 2        # Echo to output device 2
    OUT 4        # Also display on LEDs
    
    # Check for exit condition (ASCII 'Q' = 81)
    STR 20       # Store input character
    ADD 21       # Add -81 to check for 'Q'
    SNA          # Skip if not zero (not 'Q')
    JMP EXIT     # Exit if 'Q' pressed
    
    CLR          # Clear for next iteration
    JMP MAIN_LOOP # Continue loop

EXIT:
    CLR
    ADD 22       # Load "DONE" message start
    OUT 2        # Output 'D'
    HLT

# Data section  
ORG 20
DATA 0       # Input character storage
DATA 175     # -81 in two's complement (256-81)
DATA 68      # 'D' for DONE message
            ''',
            'expected_output': 'Echoes input until Q is pressed',
            'concepts': ['I/O operations', 'Device flags', 'Input processing']
        }
        
        self.examples['data_processing'] = {
            'name': 'Data Processing',
            'description': 'Process array of data (find maximum value)',
            'difficulty': 'Advanced',
            'code': '''
# Data Processing - Find maximum value in array
CLR
STR 30       # Initialize max value to 0
STR 31       # Initialize array index to 0

LOOP:
    CLR
    ADD 31       # Get current index
    ADD 20       # Add base address to get current element address
    STR 32       # Store address for indirect access
    
    # This is a limitation - we need indirect addressing
    # For simplicity, we'll check specific locations
    ADD 31       # Get index again
    SNA          # Skip if not first element (index 0)
    JMP CHECK_0
    
    CMP          # Get index-1  
    ADD 33       # Add 1 back
    SNA          # Skip if not second element
    JMP CHECK_1
    
    # Continue for remaining elements...
    JMP END      # For simplicity, only check first 2 elements

CHECK_0:
    CLR
    ADD 20       # Load first data element
    JMP COMPARE

CHECK_1:
    CLR
    ADD 21       # Load second data element
    JMP COMPARE

COMPARE:
    STR 34       # Store current value
    ADD 35       # Add negative of current max
    SNA          # Skip if current > max (result non-zero)
    JMP NEXT     # Current <= max, continue
    
    # New maximum found
    CLR
    ADD 34       # Load current value
    STR 30       # Update maximum

NEXT:
    CLR
    ADD 31       # Get current index
    ADD 33       # Add 1
    STR 31       # Update index
    ADD 36       # Add -2 (check if we've processed 2 elements)
    SNA          # Skip if more elements to process
    JMP END      # All elements processed
    JMP LOOP     # Continue loop

END:
    CLR
    ADD 30       # Load maximum value
    OUT 4        # Display on LEDs
    HLT

# Data array
ORG 20
DATA 42      # Element 0
DATA 99      # Element 1 (this should be the maximum)

# Variables
ORG 30
DATA 0       # Maximum value storage
DATA 0       # Array index
DATA 0       # Current address storage  
DATA 1       # Constant 1
DATA 0       # Current value temp storage
DATA 0       # Negative of current max (updated in loop)
DATA 254     # -2 in two's complement
            ''',
            'expected_output': 'Maximum value (99) displayed on LEDs',
            'concepts': ['Arrays', 'Data processing', 'Comparisons', 'Complex loops']
        }
    
    def setup_tutorials(self):
        """Setup tutorial lessons"""
        
        self.tutorials['lesson_1'] = {
            'title': 'Lesson 1: Basic Instructions',
            'description': 'Learn the fundamental MICRO II instructions',
            'content': '''
# MICRO II Tutorial - Lesson 1: Basic Instructions

The MICRO II has 16 instructions divided into categories:

## Memory Reference Instructions (with optional indirect addressing):
- JMP addr   : Jump to address
- STR addr   : Store accumulator to address  
- ADD addr   : Add memory contents to accumulator

## Register/Control Instructions:
- CLR        : Clear accumulator
- CMP        : Complement accumulator (1's complement)
- RTL        : Rotate accumulator left
- RTR        : Rotate accumulator right
- ORS        : OR data switches into accumulator
- NOP        : No operation
- HLT        : Halt execution

## Skip Instructions:
- SNO        : Skip if no overflow
- SNA        : Skip if accumulator non-zero
- SZS        : Skip if sign bit = 0

## I/O Instructions:
- SFG dev    : Skip if device flag set
- INP dev    : Input from device
- OUT dev    : Output to device

## Exercise: Try this simple program:
            ''',
            'exercise': '''
CLR          # Clear the accumulator
ADD 10       # Add contents of address 10
STR 11       # Store result in address 11
HLT          # Stop execution

# Data section
ORG 10
DATA 42      # Our test value
DATA 0       # Result will be stored here
            ''',
            'explanation': '''
This program:
1. Clears the accumulator (AC = 0)
2. Adds the value at address 10 (42) to AC (AC = 42)
3. Stores AC contents to address 11
4. Halts execution

After running, address 11 should contain 42.
            '''
        }
        
        self.tutorials['lesson_2'] = {
            'title': 'Lesson 2: Memory Organization',
            'description': 'Understanding MICRO II memory layout',
            'content': '''
# MICRO II Tutorial - Lesson 2: Memory Organization

The MICRO II uses an 8-bit address space (256 words total).
Memory is organized in pages:

## Memory Layout:
- 8 pages of 32 words each
- Each word is 8 bits
- Page 0: addresses 00-1F (0-31)
- Page 1: addresses 20-3F (32-63)
- ...
- Page 7: addresses E0-FF (224-255)

## Direct Addressing:
- Uses 5-bit address field (0-31)
- Can only address current page
- Address calculation: current_page | 5_bit_address

## Indirect Addressing:
- Indicated by * or () in assembly
- 5-bit field points to address containing actual address
- Allows access to any memory location

## Exercise: Direct vs Indirect addressing
            ''',
            'exercise': '''
# Direct addressing example
CLR
ADD 10       # Direct: adds contents of address 10
STR 11       # Direct: stores to address 11
HLT

# Indirect addressing example  
CLR
ADD *12      # Indirect: address 12 contains pointer to actual data
STR *13      # Indirect: address 13 contains pointer to destination
HLT

# Data section
ORG 10
DATA 25      # Direct data
DATA 0       # Direct result
DATA 100     # Pointer to address 100
DATA 101     # Pointer to address 101

# Indirect data section
ORG 100
DATA 50      # Indirect data
DATA 0       # Indirect result
            ''',
            'explanation': '''
Direct addressing: Instruction contains actual address
Indirect addressing: Instruction contains address of pointer

Direct is faster but limited to current page.
Indirect is slower but can access any memory location.
            '''
        }
        
        self.tutorials['lesson_3'] = {
            'title': 'Lesson 3: Control Flow',
            'description': 'Implementing loops and conditional logic',
            'content': '''
# MICRO II Tutorial - Lesson 3: Control Flow

The MICRO II provides conditional execution through skip instructions:

## Skip Instructions:
- SNO: Skip if no overflow (clears overflow flag)
- SNA: Skip if accumulator is non-zero
- SZS: Skip if sign bit is zero (bit 7 = 0)

## Common Patterns:

### Simple Loop:
LOOP:
    # loop body
    SNA      # Skip if AC != 0
    JMP LOOP # Continue if AC == 0

### Conditional Execution:
    ADD something
    SNA          # Skip if result != 0
    JMP zero_case # Handle zero case
    # Handle non-zero case
zero_case:
    # Handle zero case

## Exercise: Counting loop
            ''',
            'exercise': '''
# Count from 1 to 3 and stop
CLR
STR 20       # Initialize counter to 0

LOOP:
    ADD 21       # Add 1 to counter
    STR 20       # Update counter
    OUT 4        # Display current count on LEDs
    
    # Check if count reached 3
    STR 22       # Save count for comparison
    ADD 23       # Add -3 
    SNA          # Skip if not zero (haven't reached 3)
    JMP END      # Exit if reached 3
    
    CLR          # Clear AC
    ADD 20       # Reload counter
    JMP LOOP     # Continue

END:
    HLT

# Data
ORG 20
DATA 0       # Counter
DATA 1       # Increment
DATA 0       # Temp storage
DATA 253     # -3 in two's complement (256-3)
            ''',
            'explanation': '''
This loop demonstrates:
1. Counter initialization
2. Loop body execution
3. Conditional termination using SNA
4. Two's complement arithmetic for comparison

The loop will count 1, 2, 3 then stop.
            '''
        }
        
        self.tutorials['lesson_4'] = {
            'title': 'Lesson 4: Input/Output',
            'description': 'Working with I/O devices',
            'content': '''
# MICRO II Tutorial - Lesson 4: Input/Output

The MICRO II supports up to 8 I/O devices (addresses 0-7):

## Device Addresses:
- 0: Memory bank selection (special case)
- 1: Console input
- 2: Console output  
- 3: Data switches
- 4: LED display
- 5: Paper tape
- 6-7: Available for custom devices

## I/O Instructions:
- SFG dev: Skip if device flag is set (device ready)
- INP dev: Input data from device (ORs with AC)
- OUT dev: Output AC data to device

## Device Flags:
Each device has a flag indicating readiness:
- Input devices: flag set when data available
- Output devices: flag set when ready to accept data

## Exercise: Simple I/O program
            ''',
            'exercise': '''
# I/O Example: Read switches, process, display
CLR

# Read data switches  
INP 3        # Input from data switches device
STR 20       # Store original value

# Process the data (complement it)
CMP          # Complement the value
STR 21       # Store processed value

# Output to multiple devices
OUT 2        # Send to console
OUT 4        # Send to LED display

# Show original value too
CLR
ADD 20       # Load original
OUT 2        # Send to console

HLT

# Storage
ORG 20  
DATA 0       # Original value
DATA 0       # Processed value
            ''',
            'explanation': '''
This program:
1. Reads value from data switches
2. Complements the value 
3. Outputs both original and processed values
4. Demonstrates multiple output devices

Try setting different switch values and observe outputs.
            '''
        }
    
    def get_example(self, name):
        """Get a specific example program"""
        return self.examples.get(name)
    
    def get_tutorial(self, name):
        """Get a specific tutorial lesson"""
        return self.tutorials.get(name)
    
    def list_examples(self):
        """List all available examples"""
        examples_list = []
        for name, example in self.examples.items():
            examples_list.append({
                'name': name,
                'title': example['name'],
                'description': example['description'],
                'difficulty': example['difficulty'],
                'concepts': example['concepts']
            })
        return examples_list
    
    def list_tutorials(self):
        """List all available tutorials"""
        tutorials_list = []
        for name, tutorial in self.tutorials.items():
            tutorials_list.append({
                'name': name,
                'title': tutorial['title'],
                'description': tutorial['description']
            })
        return tutorials_list
    
    def get_all_examples(self):
        """Get all example programs"""
        return self.examples
    
    def get_all_tutorials(self):
        """Get all tutorial lessons"""
        return self.tutorials
    
    def create_interactive_lesson(self, lesson_name):
        """Create an interactive lesson with step-by-step guidance"""
        if lesson_name not in self.tutorials:
            return None
        
        tutorial = self.tutorials[lesson_name]
        
        return {
            'title': tutorial['title'],
            'description': tutorial['description'],
            'content': tutorial['content'],
            'exercise': tutorial.get('exercise', ''),
            'explanation': tutorial.get('explanation', ''),
            'steps': self._create_lesson_steps(tutorial)
        }
    
    def _create_lesson_steps(self, tutorial):
        """Create step-by-step instructions for a tutorial"""
        steps = [
            {
                'step': 1,
                'title': 'Read the Concept',
                'instruction': 'Read through the tutorial content to understand the concepts.',
                'action': 'review'
            },
            {
                'step': 2,
                'title': 'Load the Exercise',
                'instruction': 'Load the exercise code into the emulator.',
                'action': 'load_code'
            },
            {
                'step': 3,
                'title': 'Analyze the Code',
                'instruction': 'Study each instruction and predict what will happen.',
                'action': 'analyze'
            },
            {
                'step': 4,
                'title': 'Run the Program',
                'instruction': 'Execute the program and observe the results.',
                'action': 'execute'
            },
            {
                'step': 5,
                'title': 'Verify Results',
                'instruction': 'Check that the results match the explanation.',
                'action': 'verify'
            },
            {
                'step': 6,
                'title': 'Experiment',
                'instruction': 'Try modifying the code to test your understanding.',
                'action': 'experiment'
            }
        ]
        return steps


# Quick reference guide
QUICK_REFERENCE = """
MICRO II Quick Reference Guide
==============================

INSTRUCTION SET:
Memory Reference (with indirect * ):
  JMP addr    - Jump to address
  STR addr    - Store AC to address  
  ADD addr    - Add memory to AC

Register/Control:
  CLR         - Clear accumulator
  CMP         - Complement AC
  RTL         - Rotate AC left
  RTR         - Rotate AC right
  ORS         - OR switches to AC
  NOP         - No operation
  HLT         - Halt

Skip Instructions:
  SNO         - Skip if no overflow
  SNA         - Skip if AC non-zero
  SZS         - Skip if sign bit = 0

I/O Instructions:
  SFG dev     - Skip if device flag set
  INP dev     - Input from device
  OUT dev     - Output to device

ASSEMBLY DIRECTIVES:
  ORG addr    - Set assembly address
  DATA value  - Define data word
  # comment   - Comment line

ADDRESSING:
  Direct:     ADD 15     (page-relative)
  Indirect:   ADD *15    (through pointer)

MEMORY LAYOUT:
  256 words (8 pages × 32 words)
  Page 0: 00-1F, Page 1: 20-3F, etc.

DEVICE ADDRESSES:
  0: Memory bank select
  1: Console input
  2: Console output
  3: Data switches
  4: LED display
  5: Paper tape
"""


def print_quick_reference():
    """Print the quick reference guide"""
    print(QUICK_REFERENCE)


if __name__ == "__main__":
    examples = MICRO2_Examples()
    
    print("MICRO II Examples and Tutorials")
    print("=" * 40)
    
    print("\nAvailable Examples:")
    for example in examples.list_examples():
        print(f"  {example['name']}: {example['title']}")
        print(f"    {example['description']} [{example['difficulty']}]")
    
    print("\nAvailable Tutorials:")
    for tutorial in examples.list_tutorials():
        print(f"  {tutorial['name']}: {tutorial['title']}")
        print(f"    {tutorial['description']}")
    
    print("\n" + "=" * 40)
    print_quick_reference()
