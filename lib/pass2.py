#
#   Pass 2
#   Pass 2 takes a constructed lst record containing memory address locations for instructions in a proposed
#       SIC/XE program.
#
#   Pass 2 attempts to generate object codes for each line item in the lst file.
#
from lib import util, symbol_table
import copy


#
#   Process Function
#   This function provides the starting point for the Pass 2
#
def process(lst):
    success = True
    program_counter = 0
    base_address = None
    new_lst = copy.deepcopy(lst)
    j = 0

    #
    #   Process Function
    #   We iterate over each line in the processed lst file to determine lines which need object code,
    #       and we generate the appropriate object code
    #
    for i, lst_item in enumerate(lst):

        if 'Error' not in lst_item:

            next_item = None
            if i+1 is not len(lst):
                next_item = lst[i+1]

            #
            #   Increment Program Counter
            #   We must increase our Program Counter past our current memory location by the size of the next operation
            #       and we generate the appropriate object code
            #
            if next_item is not None and 'Location' in next_item and len(next_item['Location'].strip()) > 0:
                program_counter = int(next_item['Location'], 16)

            meta = None
            if lst_item['Meta'] is not None:
                meta = lst_item['Meta']

            #
            #   Process Non-Object-Code Operations
            #   We process Comments, erroneous operations and Base registration early
            #
            if meta.get('flag', None) == '-comm':
                new_lst[j]['Object Code'] = ''

            elif meta.get('flag', None) == '-notop':
                new_lst[j]['Object Code'] = ''
                util.add_lst_error(lst_item['Line ID'], "Unsupported opcode found in statement", new_lst, j+1)
                j += 1
                success = False

            # Check for Base registration
            elif meta.get('mneumonic', None) == 'BASE':
                symbol_read = symbol_table.read_symbol(meta.get('operand', None))
                if symbol_read['success']:
                    base_address = int(symbol_read['tokens'][1], 16)

            elif 'operation' in meta and meta['operation'].opcode is None:
                new_lst[j]['Object Code'] = ''

            #
            #   Process Object-Code Operations
            #   We process Operations which are likely to generate Object Code
            #
            elif meta is not None:

                # Process RESW and RESB
                if meta['mneumonic'] in ['RESW', 'RESB']:
                    new_lst[j]['Object Code'] = ''

                # Process BYTEs
                elif meta['mneumonic'] == 'BYTE':
                    literal = meta['operand'][1:].replace("'", '')
                    if meta['operand'][:1] == 'X' or lst_item['Object Code'] == '-lithx':
                        if len(literal) % 2 == 0:
                            new_lst[j]['Object Code'] = literal
                        else:
                            new_lst[j]['Object Code'] = ''
                            util.add_lst_error(lst_item['Line ID'], "Odd number of X bytes found in operand field: "
                                               + meta['operand'], new_lst, j+1)
                            j += 1
                            success = False
                    elif meta['operand'][:1] == 'C' or lst_item['Object Code'] == '-litch':
                        new_lst[j]['Object Code'] = "".join([hex(ord(c))[2:] for c in literal])

                # Process WORDs
                elif meta['mneumonic'] == 'WORD':
                    new_lst[j]['Object Code'] = util.hexized(meta['operand'], 6)

                # Process generic operations with opcodes
                else:
                    opcode = int(meta['operation'].opcode, 16)
                    register_operation = (2 in meta['operation'].format_list)

                    # Process ni bits
                    if meta['sic'] or register_operation:  # register-to-register operations and SIC operations
                        ni_value = 0
                    elif meta['addressing'] == '#':  # immediate addressing
                        ni_value = 1
                    elif meta['addressing'] == '@':  # indirect addressing
                        ni_value = 2
                    else:                            # most operations
                        ni_value = 3

                    new_lst[j]['Object Code'] = hex(opcode + ni_value)[2:].zfill(2)

                    # Process xbpe bits
                    # Here, we determine the addressing techniques used by the operation,
                    #   and generate the appropriate object based on such
                    xbpe_value = 0

                    if meta['indexed']:
                        xbpe_value = 8

                    # SIC operations
                    if meta['sic']:
                        xbpe_value = 0
                        symbol_read = symbol_table.read_symbol(meta['operand'])
                        address = symbol_read['tokens'][1]

                        # address is already hex
                        new_lst[j]['Object Code'] += hex(xbpe_value)[2:] + str(address).zfill(3)

                    # extended operations
                    elif meta['extended']:
                        xbpe_value += 1
                        symbol_read = symbol_table.read_symbol(meta['operand'])
                        address = symbol_read['tokens'][1].zfill(5)

                        # address is already hex
                        new_lst[j]['Object Code'] += hex(xbpe_value)[2:] + str(address).zfill(3)

                    # register to register operations, no addressing necessary
                    elif register_operation:
                        registers = meta['operand'].split(',')
                        address = ""
                        if len(registers) > 0:
                            address += util.lookup_register(registers[0])
                        if len(registers) > 1:
                            address += util.lookup_register(registers[1])
                        else:
                            address += "0"

                        new_lst[j]['Object Code'] += str(address).zfill(2)  # register address is less than 9

                    # process immediate addressing
                    elif meta['addressing'] == '#':
                        address = hex(int(meta['operand']))[2:]
                        new_lst[j]['Object Code'] += str(address).zfill(4)  # address is already hex

                    # process RSUB
                    elif meta['mneumonic'] == 'RSUB':
                        address = '0000'
                        new_lst[j]['Object Code'] += str(address).zfill(4)  # address is already hex

                    # start PC/Base relative operations
                    else:
                        symbol_read = symbol_table.read_symbol(meta['operand'])
                        if symbol_read['success']:
                            if 'tokens' in symbol_read:
                                if len(symbol_read['tokens']) > 1:
                                    xbpe_value += 2

                                    # calculate relative address
                                    address = int(symbol_read['tokens'][1], 16) - program_counter

                                    # is positive PC relative
                                    if 0 <= address < 2048:
                                        new_lst[j]['Object Code'] += hex(xbpe_value)[2:] + hex(address)[2:].zfill(3)
                                    # is negative PC relative
                                    elif -2048 <= address < 0:
                                        new_lst[j]['Object Code'] += hex(xbpe_value)[2:] + util.hexized(address, 3)
                                    # is Base relative
                                    else:
                                        if base_address:
                                            xbpe_value += 2
                                            address = int(symbol_read['tokens'][1], 16) - base_address
                                            if 0 <= address <= 4097:
                                                new_lst[j]['Object Code'] += hex(xbpe_value)[2:] + util.hexized(address, 3)
                                            else:
                                                new_lst[j]['Object Code'] = ''
                                                util.add_lst_error(lst_item['Line ID'], "Address out of range, no BASE...", new_lst, j+1)
                                                j += 1
                                                success = False
                                        else:
                                            new_lst[j]['Object Code'] = ''
                                            util.add_lst_error(lst_item['Line ID'], "Address out of range, no BASE...", new_lst, j+1)
                                            j += 1
                                            success = False
                        else:
                            new_lst[j]['Object Code'] = ''
                            util.add_lst_error(lst_item['Line ID'], symbol_read['message'], new_lst, j+1)
                            j += 1
                            success = False

                # clean up Object Code output, uppercase with all white space to the right
                if 'Error' not in new_lst[j]:
                    new_lst[j]['Object Code'] = new_lst[j]['Object Code'].strip().upper().ljust(8)

        j += 1

    del lst
    return {
        "lst": new_lst,
        "success": success
    }