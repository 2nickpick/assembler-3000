#
#
#   Symbol Table
#   The Symbol Table stores labels and memory addresses for those labels in an efficient manor.
#
#   New Labels or constants are processed and stored according to their hash value
#       (determined via the util.my_hash function)
#
#
#

from lib import util

__author__ = 'Nicholas Pickering'

hash_table_size = 50
symbol_table = dict()
SYMBOL_DEBUG = False


#
# Write Symbol Function
# insert a label, or constant, into the Symbol Table
#
# label - proposed label, or identifier, for the address to be stored in the symbol table
# value - memory address location to be stored against label
#
# This function may return True or False to denote success and failure, along with a message
#   to provide additional information about an error, or success.
#
def write_symbol(label, value):

    # Produce a hash value from the token
    hash_value = util.my_hash(label, hash_table_size)
    initial_hash_value = hash_value

    response = {
        'success': True,
        'message': None
    }

    # Put token in table according to its hash value, adjusting linearly for collisions
    while hash_value in symbol_table.keys():
        tokens_read = symbol_table[hash_value].split()

        # If token read from the table is the same as the token read from the file
        # then error out of the loop
        if tokens_read[0] == label:
            response = {
                'success': False,
                'message': 'Duplicate label found, ' + label
            }
            break

        # Adjust linearly for collision detected
        if hash_value != hash_table_size-1:
            hash_value += 1
        else:
            hash_value = 0

        if hash_value == initial_hash_value:
            response = {
                'success': False,
                'message': 'Symbol table is full'
            }
            break

    # If no error occurred, then write the value at the current hash value
    if response['success']:
        symbol_table[hash_value] = label + " " + hex(value)[2:].upper().zfill(5)

    return response


#
# Read Symbol Function
# look up a label, or constant, from the Symbol Table
#
# label - label, or identifier, to retrieve a memory location for
#
# This function may return True or False to denote success and failure, along with a message
#   to provide additional information about an error, or success.
#
# This function also returns the token in the symbol table.
#
def read_symbol(label):

    # Produce a hash value from the token
    hash_value = util.my_hash(label, hash_table_size)

    # Find a token and its value from the table
    if hash_value in symbol_table.keys():
        tokens_read = symbol_table[hash_value].split()

        response = {
            'success': True,
            'message': "Operand found successfully",
            'tokens': tokens_read
        }

        while str(tokens_read[0]) != label:

            # Adjust linearly for collision detected
            if hash_value != hash_table_size:
                hash_value += 1
            else:
                hash_value = 0

            # If there is no token at location after linearly probing, the token is not in the table
            # Error out of the loop
            if hash_value not in symbol_table.keys():
                response = {
                    'success': False,
                    'message': "Operand not found in symbol table",
                    'tokens': None
                }
                break
            # Else, there is a next token, so start processing it
            else:
                tokens_read = symbol_table[hash_value].split()
                response = {
                    'success': True,
                    'message': "Operand found successfully",
                    'tokens': tokens_read
                }

    else:
        response = {
            'success': False,
            'message': "Operand not found in symbol table",
            'tokens_read': None
        }

    return response

#
# Print Symbols Function
# quick and dirty dump of Symbol Table
#
def print_symbols():
    print("Printing Symbol Table...")
    symbol_table_sorted = sorted(symbol_table)
    for symbol in symbol_table_sorted:
        symbol_tokens = symbol_table[symbol].split()

        extra_tab = ""
        if len(symbol_tokens[0]) < 8:
            extra_tab = "\t"

        print(str(symbol) + "\t" + symbol_tokens[0] + "\t" + extra_tab + symbol_tokens[1])