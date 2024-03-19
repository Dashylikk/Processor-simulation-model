class CPU:
    def __init__(self):
        self.registers = {
            'R1': [0] * 22,
            'R2': [0] * 22,
            'R3': [0] * 22,
            'R4': [0] * 22,
            'R5': [0] * 22,
            'R6': [0] * 22,
            'R7': [0] * 22,
            'R8': [0] * 22,
            'R9': [0] * 22,
            'R10': [0] * 22
        }
        self.PC = 1
        self.TC = 0
        self.PS = 0
        self.status_register = [0]
        self.accumulator = [0] * 22
        self.memory = [0] * (2 ** 22)
        self.IR = ''

        self.print_state()

    def print_state(self):
        if self.IR:
            print("CPU State:")
            print(f"IR = {self.IR}")
            print(f"PC = {self.PC} TC = {self.TC} PS = {self.PS}")
            print(f"Acc = {self.bits_byte_format(self.accumulator)}")
            for register, value in self.registers.items():
                print(f"{register} = {self.bits_byte_format(value)}")
            print("." * 30)

    def bits_byte_format(self, bits):
        return ' '.join([''.join(map(str, bits[i:i + 8])) for i in range(0, 22, 8)])

    def check_overflow(self, bits):
        max_value = 2 ** 22 - 1
        value = 0
        for bit in bits:
            value = (value << 1) | bit

        if value > max_value:
            self.PS = 1
        else:
            self.PS = 0

    def execute_instruction_tact_by_tact(self, raw_command):
        try:
            split_command = raw_command.split()
            command = split_command[0]
            self.IR = raw_command
        except (ValueError, IndexError):
            print("Invalid command format")
            return
        self.TC = 1
        self.print_state()

        if command == 'mov':
            if len(split_command) == 2:
                operand = split_command[1]

                if operand.isdigit() or (operand[0] == '-' and operand[1:].isdigit()):
                    operand = int(operand)
                    operand_binary = bin(operand & 0x3FFFFF)[2:].zfill(22)
                    operand = [int(bit) for bit in operand_binary]

                    self.accumulator = operand
                    self.check_overflow(operand)
                elif operand in self.registers:
                    self.registers[operand] = self.accumulator
                else:
                    print("Invalid operand or register name format")
                    self.PS = 1
            else:
                print("Invalid number of operands for mov command")
                self.PS = 1


        elif command == 'add':
            if len(split_command) == 2:
                source_register = split_command[1]

                if source_register in self.registers:
                    carry = 0
                    temp_accumulator = self.accumulator.copy()
                    for i in range(21, -1, -1):
                        sum_bits = self.accumulator[i] + self.registers[source_register][i] + carry
                        carry = sum_bits // 2
                        temp_accumulator[i] = sum_bits % 2
                    self.status_register[0] = carry
                    self.accumulator = temp_accumulator
                    self.check_overflow(temp_accumulator)
                else:
                    print(f"Invalid register name: {source_register}")
                    self.PS = 1
            else:
                print("Invalid number of operands for add command")
                self.PS = 1


        elif command == 'str':

            if len(split_command) == 2:

                destination_location = split_command[1]

                if destination_location.lower() == "upper" or destination_location.lower() == "lower":

                    is_upper = destination_location.lower() == "upper"

                    operand_data = int(''.join(map(str, self.accumulator)), 2)

                    if (65 <= operand_data <= 90 or 97 <= operand_data <= 122):

                        if (is_upper and 97 <= operand_data <= 122) or (not is_upper and 65 <= operand_data <= 90):
                            operand_data = operand_data - 32 if is_upper else operand_data + 32

                    else:

                        print("Invalid value for the second operand in the str command")

                        self.PS = 1

                        operand_data = 0  # Анулюємо аккумулятор

                    operand_bits = list(f'{operand_data:08b}')

                    operand_bits = [int(bit) for bit in operand_bits]

                    operand_bits = [0] * (22 - len(operand_bits)) + operand_bits

                    self.accumulator = operand_bits

                    self.check_overflow(operand_bits)

                else:

                    print("Invalid value for the second operand in the str command")

                    self.PS = 1

            else:

                print("Invalid number of operands for str command")

                self.PS = 1

        self.check_overflow(self.accumulator)

        for register in self.registers.values():
            self.check_overflow(register)

        self.TC = 2

        self.print_state()

        self.PC += 1

    def execute_from_file(self, file_path):
        with open(file_path, 'r') as file:
            commands = file.readlines()
            for command in commands:
                command = command.strip()
                if command == 'exit':
                    break
                else:
                    self.execute_instruction_tact_by_tact(command)

if __name__ == '__main__':
    cpu = CPU()

    file_path = "commands.txt"
    cpu.execute_from_file(file_path)
