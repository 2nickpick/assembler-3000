#
#
#   Assemble
#   This module acts as the starting point for the assembler
#
#   The goal of this project is to translate a SIC/XE program into object code.
#   The program accepts a file containing a SIC/XE program to process
#       in 2 passes. The process behind each pass is described in detail later.
#
#   After both passes, or after a fatal error, the module generates an lst file. The lst file contains a description
#       of the result of the assembly.
#
#   If pass 2 is successful, then an obj file is generated. The obj file contains the assembled object code of
#       the original program.
#
#
from lib import util, pass1, pass2

__author__ = 'Nicholas Pickering'

import sys
import datetime
import os

location = 0
filename = ''
generate_obj = False

#   Start Main Program
print("SIC/XE Assembler 3000")
print("Written by Nicholas Pickering")

#   Read in file for processing...
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    util.error("No filename specified... Exiting...", True)

file = open(filename, "r")
if not file:
    util.error("File could not be loaded... Exiting...", True)

#
#   Start Pass 1
#   Generate Memory Locations for input program
#
pass1_result = pass1.process(file)
lst = pass1_result['lst']

if pass1_result['success'] is False:
    print("Errors (pass 1): No object code generated. Refer to "+filename+".lst.")
else:
    #
    #   Start Pass 2
    #   Generate Object Code for input program, only if Pass 1 is successful
    #
    pass2_result = pass2.process(pass1_result['lst'])
    lst = pass2_result['lst']

    if pass2_result['success'] is False:
        print("Errors (pass 2): partial object code generation, but no object file instantiation. Refer to "+filename+".lst.")
    else:

        #
        #   Assembly Successful
        #   Pass 1 and 2 completed successfully, allow for generation of obj file
        #
        generate_obj = True
        print("Assembly report file: "+filename+".lst")
        print("         object file: "+filename+".obj")


#
#   Write lst File
#   Compile each of the lst line items into a file
#
lst_filename = filename+".lst"

if os.path.exists(lst_filename):  # remove file if exists
    os.remove(lst_filename)

with open(lst_filename, "w") as lst_file:
    lst_file.write("******************************************************" + "\n")
    lst_file.write("SIC/XE Assembler 3000" + "\n")
    lst_file.write("Written by Nicholas Pickering" + "\n")
    lst_file.write("Generated: " + datetime.datetime.now().__format__('%a %b %d %H:%M:%S %Y') + "\n")
    lst_file.write("******************************************************" + "\n")
    lst_file.write("ASSEMBLER REPORT" + "\n")
    lst_file.write("----------------" + "\n")
    lst_file.write("    \tLocation\tObject Code\t\tSource Code" + "\n")
    lst_file.write("    \t--------\t-----------\t\t-----------" + "\n")
    for lst_item in lst:
        if 'Error' not in lst_item:
            lst_file.write(lst_item['Line ID'] + "\t\t" + lst_item['Location'].ljust(5) +
                           "\t\t" + lst_item['Object Code'].ljust(8) + "\t\t" + lst_item['Source'] + "\n")
        else:
            lst_file.write("******************* ERROR: " + lst_item['Error'] + "\n")

#
#   Write obj File
#   If assembly completed successfully, compile obj file from lst line items
#
if generate_obj:
    obj_filename = filename+".obj"

    if os.path.exists(obj_filename):  # remove file if exists
        os.remove(obj_filename)

    with open(obj_filename, "w") as obj_file:

        #
        #   Calculate number of reservations
        #   In order to generate our obj file correctly, we need to determine how many reserved sections are
        #       required in the final result
        #
        #   Reserved sections are determined by the use of the RESW or RESB operations
        #

        start_address = None
        current_address = None
        res_count = 0
        res_total = 1
        for i, lst_item in enumerate(lst):
            mneumonic = None
            meta = lst_item.get('Meta', None)
            if meta:
                mneumonic = meta.get('mneumonic', None)

            if mneumonic in ['RESW', 'RESB']:
                res_total += 1

        #
        #   Generate obj file
        #   Parse the lst line items, writing object code and reserved sections in as necessary
        #
        #   Reserved sections are denoted using a bang(!)
        #
        for i, lst_item in enumerate(lst):
            if 'Error' not in lst_item:

                # evaluate the item after the current item in the lst
                # necessary to determine program counter value
                next_item = None
                if i+1 is not len(lst):
                    next_item = lst[i+1]

                mneumonic = None
                meta = lst_item.get('Meta', None)
                if meta:
                    mneumonic = meta.get('mneumonic', None)

                #
                # Process Reserved Section Header
                #
                # Reserved sections consist of a header and a body, essentially
                # The header consists of the memory location in which the string of object codes should
                #   be written.
                #
                if mneumonic in ['RESW', 'RESB'] or current_address is None:
                    res_count += 1

                    if mneumonic in ['RESW', 'RESB']:
                        obj_file.write("!" + "\n")

                    if next_item is not None:
                        current_address = next_item['Location']

                    if start_address is None:
                        start_address = current_address

                    obj_file.write(current_address.zfill(6) + "\n")
                    if res_count == res_total:
                        obj_file.write(start_address.zfill(6) + "\n")
                    else:
                        obj_file.write("000000".zfill(6) + "\n")

                #
                # Process Reserved Section Body record
                #
                # The body consists of any assembled object codes until the next reserved section or the end of the
                #   program.
                #
                # Object Code generated during Pass 2 is written to file as-is
                #
                elif len(lst_item['Object Code']) > 0:
                    obj_file.write(lst_item['Object Code'] + "\n")

        obj_file.write("!" + "\n")
