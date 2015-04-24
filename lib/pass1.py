#
#   Pass 1
#   Pass 1 accepts a file containing a proposed SIC/XE program.
#
#   Pass 1 attempts to process the file in order to determine memory locations for the new program.
#
from lib import util, symbol_table


#
#   Process Function
#   This function provides the starting point for the Pass 1
#
def process(file):
    lst = []
    lines_counted = 0
    literal_stack_hex = []
    literal_stack_char = []
    success = True

    #
    #   Process Input File
    #   We iterate over each line to collect information about it, to determine its relevance in the final object code
    #
    for line in file.readlines():
        line = line.replace("\n", "")

        # Check if line is a comment, if so skip
        if line[0] == '.':
            util.add_lst_record(str(lines_counted+1), '        ',
                                '', line, {"flag": "-comm"}, lst)
            lines_counted += 1
            continue

        # Check for blank lines, if so skip
        if "".join(line.split()) == "":
            continue

        # break up the line appropriately
        label = line[:7].replace(" ", "")

        extended = False
        if len(line) > 8:
            extended = line[9] == "+"

        sic = False
        if len(line) > 8:
            sic = line[9] == "*"

        mneumonic = line[10:16].replace(" ", "")

        addressing = ""
        if len(line) > 17:
            addressing = line[18]

        operand = line[19:28].replace(" ", "")

        indexed = False
        if ",X" in operand:
            operand = operand.replace(",X", "")
            indexed = True

        # lookup operation for format size
        operation = util.lookup_operation(mneumonic)

        meta = {
            "label": label,
            "mneumonic": mneumonic,
            "operation": operation,
            "operand": operand,
            "indexed": indexed,
            "extended": extended,
            "sic": sic,
            "addressing": addressing
        }

        #
        #   Add Line Items to lst File
        #   Based on information pulled from processed file, we generate memory locations for each line item
        #
        lst_record_added = False
        if not operation:
            util.add_lst_record(str(lines_counted+1), '     ',
                                '', line, {"flag": "-notop"}, lst)
            continue

        # Handle START case
        if operation.name is "START":
            if lines_counted is 0:
                location = int(operand, 16)
            else:
                util.error("START must be the first line called")
                continue

        # Handle LTORG / END literal organization
        elif operation.name in ["LTORG", "END"]:
            literal_counter = 0

            util.add_lst_record(str(lines_counted+1), str(hex(location)),
                                '', line, meta, lst)
            lst_record_added = True

            #
            #   Process Literal Stacks
            #   As we process our file, we collect literals to be allocated at LTORG or END checkpoints
            #
            #   Here, we allocate the memory and store the symbols necessary to process literals.
            #

            # Process Character Literals
            if len(literal_stack_char) > 0:
                while len(literal_stack_char):
                    literal = literal_stack_char.pop()
                    operand = "C'" + literal + "'"
                    source = "=" + operand + "\t  BYTE\t  " + operand + "\t\t.literal organization"
                    write_response = symbol_table.write_symbol(operand, location)
                    operation_size = len(literal)

                    meta = {
                        "label": source,
                        "mneumonic": "BYTE",
                        "operation": util.lookup_operation("BYTE"),
                        "operand": operand,
                        "indexed": indexed,
                        "extended": extended,
                        "sic": sic,
                        "addressing": addressing,
                        "flag": "-litch"
                    }
                    util.add_lst_record("+" + str(literal_counter+1) + "+", str(hex(location)),
                                        '', source, meta, lst)

                    if write_response['success'] is not True:
                        util.add_lst_error(str(lines_counted+1), write_response['message'], lst)
                        success = False
                        operation_size = 0

                    location += operation_size
                    literal_counter += 1

            # Process Hex Literals
            if len(literal_stack_hex) > 0:
                while len(literal_stack_hex):
                    literal = literal_stack_hex.pop()
                    operand = "X'" + literal + "'"
                    source = "=" + operand + "\t  BYTE\t  " + operand + "\t.literal organization"
                    write_response = symbol_table.write_symbol(operand, location)
                    operation_size = int(len(literal)/2)

                    meta = {
                        "label": source,
                        "mneumonic": "BYTE",
                        "operation": util.lookup_operation("BYTE"),
                        "operand": operand,
                        "indexed": indexed,
                        "extended": extended,
                        "sic": sic,
                        "addressing": addressing,
                        "flag": "-lithx"
                    }
                    util.add_lst_record("+" + str(literal_counter+1) + "+", str(hex(location)),
                                        '', source, meta, lst)

                    if write_response['success'] is not True:
                        operation_size = 0
                        util.add_lst_error(str(lines_counted+1), write_response['message'], lst)
                        success = False

                    # if hex literal is invalid, anticipate no memory increase
                    if len(literal) % 2 != 0:
                        operation_size = 0

                    location += operation_size
                    literal_counter += 1

            lines_counted += 1

        # operation is valid, if label exists add it to the symbol table

        #
        #   Store Label in Symbol Table
        #   If an operation is deemed valid and the source line contains a label for the instruction,
        #       we add the label to the symbol table.
        #
        if len(label) > 0:

            # check for a label to store
            write_response = symbol_table.write_symbol(label, location)

            if write_response['success'] is not True:
                util.add_lst_error(str(lines_counted+1), write_response['message'], lst)
                success = False

        # add line to lst record, if it hasn't already been added
        if not lst_record_added:
            util.add_lst_record(str(lines_counted+1), str(hex(location)),
                                '', line, meta, lst)

            #
            #   Determine Memory Location of Next Operation
            #   We increment our current memory location per the current operation's size
            #
            #   Here, we must also process dynamically sized operations such as BYTE operations, and operations
            #       with several formats (extended operations).
            #
            operation_size = 0
            if operation.opcode is None:
                pass
            elif len(operation.format_list) is 0:
                # operation_size must be calculated
                if extended:
                    util.error("Operation is marked as extended, but extended version is not available...")
                    continue
                else:
                    if operation.name is "RESW":
                        operation_size = int(operand) * 3
                    elif operation.name is "RESB":
                        operation_size = int(operand)
                    elif operation.name is "BYTE":
                        literal = operand[1:].replace("'", '')
                        if operand[:1] == 'X':
                            if len(literal) % 2 == 0:
                                operation_size = int(len(literal)/2)
                            else:
                                util.add_lst_error(str(lines_counted+1),
                                                   "Odd number of X bytes found in operand field", lst)
                                success = False
                        elif operand[:1] == 'C':
                            operation_size = len(literal)
                        else:
                            util.error("Malformed operand: " + operand[:1] + "...")
            else:
                operation_size = operation.format_list[0]
                if extended:
                    if len(operation.format_list) > 1:
                        operation_size = operation.format_list[1]
                    else:
                        operation_size = 0
                        util.error("Operation is marked as extended, but extended version is not available...")

            location += operation_size

            #
            #   Process Literals to Stacks
            #   If an operation's operand consists of a literal, we must store it temporarily on a stack and
            #       process its memory location later.
            #
            if addressing == '=':
                if len(operand) > 0:
                    literal = operand[1:].replace("'", '')
                    if operand[0] == 'C':
                        literal_stack_char.append(literal)
                    elif operand[0] == 'X':
                        literal_stack_hex.append(literal)

            # done processing a line of code to be assembled, increment lines counted
            lines_counted += 1

    return {
        "lst": lst,
        "success": success
    }