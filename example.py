import ScPatternSelect
import socket

host_message = """--- WARNING ---
This exapmle contains code that when ran 
will change the rate on prod if ran there

The code that will change the rate is 
commented out by default

To run the example and develop with 
this code use lcls-dev3 as it contains 
the test stand and you will have read/write
permission on all pvs without affecting prod
"""

# Double check that this example is being ran on lcls-dev3
# not recomended: Comment out the following code block to
# run on a different server

if socket.gethostname() != "lcls-dev3":
    print(host_message)
    exit(1)

patt_sel = ScPatternSelect.ScPatternSelect("SYS0", "1", "sioc-sys0-ts01")

"""
For most functions you will need a pattern name
ther are two ways to get pattern names, from the gui
and from functions provided in this code.

1. Via gui
navigate to the sc pattern selection gui
Use the gui to find the pattern you want
click the view pattern button
copy the name from the display into your code

2. Via get_pattern_name_by_rate() function
This takes in rates, and timing sources for each destination
or a dictionary with this information (more details below)

3. Write your own search function

"""
# how to use get_pattern_name_by_rate()

# fixed rate (FR) is the default
pattern_name = patt_sel.get_pattern_name_by_rate(sxr_rate=10)
print(f"this is a 10Hz Fixed Rate pattern to SXR: {pattern_name}")

# which means you will need to specifiy when you want AC rate
pattern_name = patt_sel.get_pattern_name_by_rate(sxr_rate=10, sxr_time_src="AC")
print(f"this is a 10Hz AC pattern to SXR: {pattern_name}\n")

# Valid destination names are stored in patt_sel.globals.DEST_NAMES
dest_names = patt_sel.globals.DEST_NAMES
print(f"Valid Dest Names: {dest_names}\n")

# you can convert between the dest number and dest names
init_dest_num = 4
dest_name = patt_sel.globals.DEST_NAMES[init_dest_num]
dasel_num = patt_sel.globals.DEST_NAMES.index("SC_DASEL")
print(f"initial destination number is: {init_dest_num}")
print(f"the destination name associated with this dest num is {dest_name}")
print(f"finding the dest num for SC_DASEL: {dasel_num}\n")

# pattern rates go by actual rate rather than 'tpg' rate
# the real_rate = tpg_rate/.98
# the real_rate is what shows up on displays, so this point can mostly be ignored
# if you do not know the rates available for the destination
# you can use the get_available_rates() function to get a list of
# available rates as integers or strings
sxr_rates = patt_sel.get_available_rates("SC_SXR", "FR")
print(f"fixed rates for sxr: {sxr_rates}")

# you can also use the dest number
sxr_rates = patt_sel.get_available_rates(4, "AC", as_string=True)
print(f"AC rates for SXR: {sxr_rates}\n")


# multiple destinations can be specified
pattern_name = patt_sel.get_pattern_name_by_rate(
    diag0_rate=10, diag0_time_src="AC", sxr_rate=102
)
print(f"This is a pattern with ac rate to diag0 and fixed rate to sxr: {pattern_name}")

# for ease of programing you can also provide a dictionary
# with dest numbers as keys and [dest_rate, dest_time_src] as values
# i.e. {1: [0, 'FR'], 2: [0, 'FR'], 3: [0, 'FR'], 4: [10, 'FR'], 5: [0, 'FR']}
# Supports partial dictionaries as well
# i.e. {4: [10, 'FR']}
# Note: providing a dictionary will override any other arguments
pattern_name = patt_sel.get_pattern_name_by_rate(
    dest_data={2: [10, "FR"], 4: [1326, "FR"]}
)
print(f"Pattern with 10Hz FR to bsyd, and 1326Hz FR to SXR: {pattern_name}")

# you do not need to provide the fallback rate for bsyd
# bsyd requires 10Hz be sent to it when the rate past bsyd is above 1020
pattern_name = patt_sel.get_pattern_name_by_rate(dest_data={4: [1326, "FR"]})
print(
    f"The same pattern as before, with bsyd automatically accounted for: {pattern_name}\n"
)


# Once you have a pattern name you can use the run_pattern function to
# Load and apply the pattern to the machiene
# This code is commented out by default so no one goes and changes the
# rate accidentaly
# Also, the PVs that are written to have channel access security on them
# So an OPI needs to run your code if you actually want to change the rate
# of the Machine
# It is recommended to use the run_pattern() function for almost all usecases
#
# self.patt_sel.run_pattern(pattern_name)

# The alternatives to run_pattern() is to use load_pattern() then apply_pattern()
# self.patt_sel.load_pattern(pattern_name)
# Apply pattern requires the pattern name as a safty procotion
# The loaded pattern and the pattern you want to apply need to be the same
# run_pattern() does both of these automatically
# self.patt_sel.apply_pattern(pattern_name)


# There are several other provided functions to help with tasks
# such as understanding the applied pattern, creating your own pattern search
# algorithyms, ect.

# Stop the beam using tpg beam classes
# patt_sel.stop_beam()

# Recover the tpg beam classes to start the beam agian
# patt_sel.tpg_beam_class_reset()

# retrieve the pattern that is running and get informaion on it
running_pattern = patt_sel.get_pattern_running()
print(f"The running pattern is: {running_pattern}")

# retrieve the data in the NTTable on the pattern that is running
# in the form of a dictionary
running_pattern_data = patt_sel.get_pattern_running_data()
print(f"It has the following data in the NTTable")
for key, value in running_pattern_data.items():
    print(f"{key}: {value}")

print("\n")
# Once you have a pattern name you can find out more about the pattern
# Check if pattern exists
non_existant_pattern = "pattern_name_that_will_never_exist"
pattern_name = patt_sel.get_pattern_name_by_rate(dest_data={4: [1326, "FR"]})

print(
    f"does '{non_existant_pattern}' exist? {patt_sel.pattern_exists(non_existant_pattern)}"
)
print(f"does '{pattern_name}' exist? {patt_sel.pattern_exists(pattern_name)}\n")

# you can get the row number for patterns -1 for non_existant patterns
print(
    f"What is the row number for '{non_existant_pattern}?' {patt_sel.get_pattern_row_num(non_existant_pattern)}"
)

print(
    f"What is the row number for '{pattern_name}?' {patt_sel.get_pattern_row_num(pattern_name)}"
)
