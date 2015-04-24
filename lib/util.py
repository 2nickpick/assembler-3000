#
#
#   Util
#   This module contains many functions and objects reused throughout the software
#
#


import sys


# My Hash Function
# Produces a hash of a string, based on a particular hash table size
#
# input_string - string to create hash value for
# hash_table_size - size of hash table, required to create a hash value that can fit into table
def my_hash(input_string, hash_table_size):
    output = 0
    for char in input_string:
        output += ord(char)

    return output % hash_table_size


# Lookup Operation Function
# Returns a whole Operation object based on a mneumonic
#
# mneumonic - the label of the operation, used to define it
def lookup_operation(mneumonic):

    if len(Operation.operation_table) <= 0:
        Operation.load_operation_table()

    if mneumonic in Operation.operation_table.keys():
        return Operation.operation_table[mneumonic]


# Lookup Register Function
# Returns the address of a register, given the register's name
#
# register - the label of the register to receive the address of
def lookup_register(register):

    if register == 'A':
        return '0'
    elif register == 'X':
        return '1'
    elif register == 'L':
        return '2'
    elif register == 'B':
        return '3'
    elif register == 'S':
        return '4'
    elif register == 'T':
        return '5'
    elif register == 'F':
        return '6'
    elif register == 'PC':
        return '8'
    elif register == 'SW':
        return '9'
    else:
        return str(int(register)-1)


# Operation class
# The Operation class defines the structure of a SIC/XE operation, providing the necessary
#   details such as formats and opcode
#
#   Formats are stored as lists, providing some operations can have one of two formats (typically 3/4)
#
class Operation:

    operation_table = dict()

    def __init__(self, name, format_list, opcode):
        self.name = name
        self.format_list = format_list
        self.opcode = opcode

    # Load Operation Table Function
    # loads all Operations into memory for lookup
    #
    @staticmethod
    def load_operation_table():

        # typical operations with assembled code
        Operation.operation_table['ADD'] = (Operation('ADD', [3, 4], '18'))
        Operation.operation_table['ADDF'] = (Operation('ADDF', [3, 4], '58'))
        Operation.operation_table['ADDR'] = (Operation('ADDR', [2], '90'))
        Operation.operation_table['AND'] = (Operation('AND', [3, 4], '40'))
        Operation.operation_table['CLEAR'] = (Operation('CLEAR', [2], 'B4'))
        Operation.operation_table['COMP'] = (Operation('COMP', [3, 4], '28'))
        Operation.operation_table['COMPF'] = (Operation('COMPF', [3, 4], '88'))
        Operation.operation_table['COMPR'] = (Operation('COMPR', [2], 'A0'))
        Operation.operation_table['DIV'] = (Operation('DIV', [3, 4], '24'))
        Operation.operation_table['DIVF'] = (Operation('DIVF', [3, 4], '64'))
        Operation.operation_table['DIVR'] = (Operation('DIVR', [2], '9C'))
        Operation.operation_table['FIX'] = (Operation('FIX', [1], 'C4'))
        Operation.operation_table['FLOAT'] = (Operation('FLOAT', [1], 'C0'))
        Operation.operation_table['HIO'] = (Operation('HIO', [1], 'F4'))
        Operation.operation_table['J'] = (Operation('J', [3, 4], '3C'))
        Operation.operation_table['JEQ'] = (Operation('JEQ', [3, 4], '30'))
        Operation.operation_table['JGT'] = (Operation('JGT', [3, 4], '34'))
        Operation.operation_table['JLT'] = (Operation('JLT', [3, 4], '38'))
        Operation.operation_table['JSUB'] = (Operation('JSUB', [3, 4], '48'))
        Operation.operation_table['LDA'] = (Operation('LDA', [3, 4], '00'))
        Operation.operation_table['LDB'] = (Operation('LDB', [3, 4], '68'))
        Operation.operation_table['LDCH'] = (Operation('LDCH', [3, 4], '50'))
        Operation.operation_table['LDF'] = (Operation('LDL', [3, 4], '70'))
        Operation.operation_table['LDL'] = (Operation('LDL', [3, 4], '08'))
        Operation.operation_table['LDS'] = (Operation('LDS', [3, 4], '6C'))
        Operation.operation_table['LDT'] = (Operation('LDT', [3, 4], '74'))
        Operation.operation_table['LDX'] = (Operation('LDX', [3, 4], '04'))
        Operation.operation_table['LPS'] = (Operation('LPS', [3, 4], 'D0'))
        Operation.operation_table['MUL'] = (Operation('MUL', [3, 4], '20'))
        Operation.operation_table['MULF'] = (Operation('MULF', [3, 4], '60'))
        Operation.operation_table['MULR'] = (Operation('MULR', [2], '98'))
        Operation.operation_table['NORM'] = (Operation('NORM', [1], 'C8'))
        Operation.operation_table['OR'] = (Operation('OR', [3, 4], '44'))
        Operation.operation_table['RD'] = (Operation('RD', [3, 4], 'D8'))
        Operation.operation_table['RMO'] = (Operation('RMO', [2], 'AC'))
        Operation.operation_table['RSUB'] = (Operation('RSUB', [3, 4], '4C'))
        Operation.operation_table['SHIFTL'] = (Operation('SHIFTL', [2], 'A4'))
        Operation.operation_table['SHIFTR'] = (Operation('SHIFTR', [2], 'A8'))
        Operation.operation_table['SIO'] = (Operation('SIO', [1], 'F0'))
        Operation.operation_table['SSK'] = (Operation('SSK', [3, 4], 'EC'))
        Operation.operation_table['STA'] = (Operation('STA', [3, 4], '0C'))
        Operation.operation_table['STB'] = (Operation('STB', [3, 4], '78'))
        Operation.operation_table['STCH'] = (Operation('STCH', [3, 4], '54'))
        Operation.operation_table['STF'] = (Operation('STF', [3, 4], '80'))
        Operation.operation_table['STI'] = (Operation('STI', [3, 4], 'D4'))
        Operation.operation_table['STL'] = (Operation('STL', [3, 4], '14'))
        Operation.operation_table['STS'] = (Operation('STS', [3, 4], '7C'))
        Operation.operation_table['STSW'] = (Operation('STSW', [3, 4], 'E8'))
        Operation.operation_table['STT'] = (Operation('STT', [3, 4], '84'))
        Operation.operation_table['STX'] = (Operation('STX', [3, 4], '10'))
        Operation.operation_table['SUB'] = (Operation('SUB', [3, 4], '1C'))
        Operation.operation_table['SUBF'] = (Operation('SUBF', [3, 4], '5C'))
        Operation.operation_table['SUBR'] = (Operation('SUBR', [2], '94'))
        Operation.operation_table['TD'] = (Operation('TD', [3, 4], 'E0'))
        Operation.operation_table['TIO'] = (Operation('TIO', [1], 'F8'))
        Operation.operation_table['TIX'] = (Operation('TIX', [3, 4], '2C'))
        Operation.operation_table['TIXR'] = (Operation('TIXR', [2], 'B8'))
        Operation.operation_table['WD'] = (Operation('WD', [3, 4], 'DC'))

        # operations with assembled code but no opcodes
        Operation.operation_table['BYTE'] = (Operation('BYTE', [], 'FF'))
        Operation.operation_table['WORD'] = (Operation('WORD', [3], 'FF'))
        Operation.operation_table['RESW'] = (Operation('RESW', [], 'FF'))
        Operation.operation_table['RESB'] = (Operation('RESB', [], 'FF'))

        # operations with no assembled codes
        Operation.operation_table['START'] = (Operation('START', [], None))
        Operation.operation_table['END'] = (Operation('END', [], None))
        Operation.operation_table['BASE'] = (Operation('BASE', [], None))
        Operation.operation_table['NOBASE'] = (Operation('NOBASE', [], None))
        Operation.operation_table['LTORG'] = (Operation('LTORG', [], None))

    def __str__(self):
        return self.name + " " + str(self.opcode) + "\n"


#   Error
#   Print Error Message to Screen
#
#   message - message to print to screen
#   do_exit - if set, error will end program. Defaults to False
def error(message, do_exit=False):
    message = "ERROR " + message
    if do_exit:
        sys.exit(message)
    else:
        print(message)


#   Add .lst Record Function
#   adds a line item to our .lst file
#
#   line_id - line number in the lst record
#   location - the memory location of the operation's final object code
#   source - the initial source which the line item was generated
#   object_code - the assembled object code for the instruction
#   meta - list which includes various information about the line item useful for assembling the object code in Pass 2
#   lst - list to add the record to
def add_lst_record(line_id, location, object_code, source, meta, lst):
    lst.append({
        'Line ID': str(line_id).zfill(3),
        'Location': str(location[2:]).zfill(5).upper(),
        'Source': str(source),
        'Object Code': str(object_code),
        'Meta': meta
    })


#   Add .lst Error Function
#   adds an error to our .lst file
#
#   line_id - line number in the lst record, will match the Line ID in order to pair error with line item
#   message - error message to write to lst file
#   lst - list to add the record to
#   inject - an optional position(integer) to inject the error message into the lst file, useful during Pass 2
def add_lst_error(line_id, message, lst, inject=False):
    record = {
        'Line ID': str(line_id).zfill(3),
        'Error': str(message)
    }

    # If a line has an error, scrap any object code generated for it
    error_found = False
    for lst_record in lst:
        if lst_record['Line ID'] == line_id:
            if 'Error' not in lst_record:
                lst_record['Object Code'] = '    '

    if not inject:
        lst.append(record)
    else:
        lst.insert(inject, record)


#   Hexized Function
#   Formats an integer into a proper hex value
#
#   Currently only supports Hex formats of size 3 and 6
#
#   operand - integer to convert to Hex-formatted String
#   size - final size of Hex-formatted String
def hexized(operand, size):
    if size == 3:
        format_string = "%03x"
        return format_string % (int(operand) & 0xfff)
    if size == 6:
        format_string = "%06x"
        return format_string % (int(operand) & 0xffffff)