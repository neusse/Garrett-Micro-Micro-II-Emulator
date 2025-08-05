# MICRO II Arithmetic Example  
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
