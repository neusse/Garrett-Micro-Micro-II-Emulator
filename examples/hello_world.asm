# MICRO II Hello World Program
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
