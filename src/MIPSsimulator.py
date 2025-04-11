"""
Módulo para emular un subconjunto de código ensamblador MIPS.

Este módulo lee un archivo de texto que contiene código ensamblador MIPS
y simula los efectos que dicho código tendría en un conjunto limitado
de registros y memoria.

Este código fue generado con el uso de Gemini 2.0 Flash
"""

#: Máximo número de instrucciones a ejecutar para evitar bucles infinitos.
MAX_INSTRUCTIONS = 40


class MIPS_Emulator:
    """
    Clase para emular la ejecución de código ensamblador MIPS.

    Soporta un conjunto limitado de instrucciones y registros.
    """

    def __init__(self, memory_size=4):
        """
        Inicializa el emulador MIPS.

        :param memory_size: El tamaño de la memoria en palabras.
        :type memory_size: int
        """
        #: Lista que representa la memoria.
        self.memory = [0] * memory_size

        #: Diccionario para los registros t0-t7.
        self.registers = {f't{i}': 0 for i in range(8)}

        #: Índice de la instrucción actual.
        self.instruction_pointer = 0

        #: Lista para almacenar las instrucciones cargadas.
        self.instructions = []

        #: Contador de instrucciones ejecutadas.
        self.instruction_count = 0

        #: Registro $0
        self.registers['zero'] = 0

    def load_instructions(self, filename: str):
        """
        Lee las instrucciones ensamblador desde un archivo.

        Cada línea del archivo se considera una instrucción.

        :param filename: La ruta al archivo que contiene el código ensamblador.
        :type filename: str
        :raises FileNotFoundError: Si el archivo especificado no se encuentra.
        """
        try:
            with open(filename, 'r') as f:
                self.instructions = [
                    line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            raise FileNotFoundError(
                f"No se pudo encontrar el archivo: {filename}")

    def run(self):
        """
        Ejecuta las instrucciones ensamblador cargadas.

        La ejecución continúa hasta que se procesan todas las instrucciones
        o se alcanza el máximo número de instrucciones permitido.
        """
        while (self.instruction_pointer < len(self.instructions)
               and self.instruction_count < MAX_INSTRUCTIONS):
            instruction = self.instructions[self.instruction_pointer]
            parts = instruction.split()
            opcode = parts[0]

            if opcode == 'add':
                self.add(parts[1], parts[2], parts[3])
            elif opcode == 'sub':
                self.sub(parts[1], parts[2], parts[3])
            elif opcode == 'lw':
                self.lw(parts[1], parts[2])
            elif opcode == 'sw':
                self.sw(parts[1], parts[2])
            elif opcode == 'addi':
                self.addi(parts[1], parts[2], parts[3])
            elif opcode == 'sll':
                self.sll(parts[1], parts[2], parts[3])
            elif opcode == 'and':
                self.and_op(parts[1], parts[2], parts[3])
            elif opcode == 'or':
                self.or_op(parts[1], parts[2], parts[3])
            elif opcode == 'nor':
                self.nor_op(parts[1], parts[2], parts[3])
            elif opcode == 'beq':
                self.beq(parts[1], parts[2], parts[3])
            elif opcode == 'bne':
                self.bne(parts[1], parts[2], parts[3])
            elif opcode == 'slt':
                self.slt(parts[1], parts[2], parts[3])
            elif opcode == 'j':
                self.jump(parts[1])
                continue  # No se incrementa contador después del j

            self.instruction_pointer += 1
            self.instruction_count += 1

        if self.instruction_count >= MAX_INSTRUCTIONS:
            print(f"Advertencia: Se alcanzó el máximo de {MAX_INSTRUCTIONS}"
                  " instrucciones. "
                  "La ejecución puede haber terminado prematuramente.")

    def get_register_value(self, register: str) -> int:
        """
        Obtiene el valor de un registro.

        :param register: El nombre del registro (ej. 't0').
        :type register: str
        :raises ValueError: Si el registro especificado no es válido.
        :returns: El valor del registro.
        :rtype: int
        """
        if register in self.registers:
            return self.registers[register]
        else:
            raise ValueError(f"Registro inválido: {register}")

    def set_register_value(self, register: str, value: int):
        """
        Establece el valor de un registro.

        :param register: El nombre del registro (ej. 't0').
        :type register: str
        :param value: El valor a establecer en el registro.
        :type value: int
        :raises ValueError: Si el registro especificado no es válido.
        """
        if register in self.registers and register != '$zero':
            self.registers[register] = value
        elif register == '$zero':
            # Do nothing, cannot write to $0
            pass
        else:
            raise ValueError(f"Registro inválido: {register}")

    def parse_memory_address(self, operand: str) -> tuple[str, int]:
        """
        Parsea un operando de acceso a memoria (ej. 'offset(register)').

        :param operand: El operando de acceso a memoria.
        :type operand: str
        :raises ValueError: Si formato de operando de memoria es incorrecto.
        :returns: Una tupla conteniendo el registro base y el offset.
        :rtype: tuple[str, int]
        """
        if '(' in operand and ')' in operand:
            offset_str, register = operand.split('(')
            register = register[:-1]
            try:
                offset = int(offset_str)
                return register, offset
            except ValueError:
                raise ValueError(f"Offset de memoria inválido: {offset_str}")
        else:
            raise ValueError(
                f"Formato de operando de memoria inválido: {operand}")

    def add(self, dest: str, src1: str, src2: str):
        """
        Implementa la instrucción 'add'.

        Suma el valor de dos registros y guarda el resultado en otro registro.

        :param dest: El registro de destino.
        :type dest: str
        :param src1: El primer registro fuente.
        :type src1: str
        :param src2: El segundo registro fuente.
        :type src2: str
        """
        dest_reg = dest.lstrip('$').strip(',')
        src1_reg = src1.lstrip('$').strip(',')
        src2_reg = src2.lstrip('$').strip(',')
        value1 = self.get_register_value(src1_reg)
        value2 = self.get_register_value(src2_reg)
        self.set_register_value(dest_reg, value1 + value2)

    def sub(self, dest: str, src1: str, src2: str):
        """
        Implementa la instrucción 'sub'.

        Resta el valor de un registro del valor de otro registro
        y guarda el resultado.

        :param dest: El registro de destino.
        :type dest: str
        :param src1: El registro del que se resta.
        :type src1: str
        :param src2: El registro a restar.
        :type src2: str
        """
        dest_reg = dest.lstrip('$').strip(',')
        src1_reg = src1.lstrip('$').strip(',')
        src2_reg = src2.lstrip('$').strip(',')
        value1 = self.get_register_value(src1_reg)
        value2 = self.get_register_value(src2_reg)
        self.set_register_value(dest_reg, value1 - value2)

    def lw(self, dest: str, address: str):
        """
        Implementa la instrucción 'lw' (load word).

        Carga una palabra desde la memoria a un registro.

        :param dest: El registro de destino.
        :type dest: str
        :param address: La dirección de memoria en formato 'offset(register)'.
        :type address: str
        """
        dest_reg = dest.lstrip('$').strip(',')
        base_reg_with_offset = address.strip(',')
        base_reg, offset = self.parse_memory_address(base_reg_with_offset)
        base_reg_stripped = base_reg.lstrip('$')
        base_address = self.get_register_value(base_reg_stripped)
        memory_index = (base_address + offset) // 4
        if 0 <= memory_index < len(self.memory):
            self.set_register_value(dest_reg, self.memory[memory_index])
        else:
            print("Error: Intento de acceder a una dirección de"
                  f" memoria inválida: {base_address + offset}")

    def sw(self, src: str, address: str):
        """
        Implementa la instrucción 'sw' (store word).

        Guarda el valor de un registro en la memoria.

        :param src: El registro fuente.
        :type src: str
        :param address: La dirección de memoria en formato 'offset(register)'.
        :type address: str
        """
        src_reg = src.lstrip('$').strip(',')
        base_reg_with_offset = address.strip(',')
        base_reg, offset = self.parse_memory_address(base_reg_with_offset)
        base_reg_stripped = base_reg.lstrip('$')
        base_address = self.get_register_value(base_reg_stripped)
        memory_index = (base_address + offset) // 4
        if 0 <= memory_index < len(self.memory):
            self.memory[memory_index] = self.get_register_value(src_reg)
        else:
            print("Error: Intento de escribir en una dirección de memoria"
                  f" inválida: {base_address + offset}")

    def addi(self, dest: str, src: str, immediate: str):
        """
        Implementa la instrucción 'addi' (add immediate).

        Suma un valor inmediato a un registro y guarda el resultado.

        :param dest: El registro de destino.
        :type dest: str
        :param src: El registro fuente.
        :type src: str
        :param immediate: El valor inmediato a sumar.
        :type immediate: str
        """
        dest_reg = dest.lstrip('$').strip(',')
        src_reg = src.lstrip('$').strip(',')
        value = self.get_register_value(src_reg)
        try:
            immediate_value = int(immediate.strip(','))
            self.set_register_value(dest_reg, value + immediate_value)
        except ValueError:
            print(f"Error: Valor inmediato inválido: {immediate}")

    def sll(self, dest: str, src: str, shamt: str):
        """
        Implementa la instrucción 'sll' (shift left logical).

        Desplaza los bits de un registro a la izquierda por una
        cantidad especificada.

        :param dest: El registro de destino.
        :type dest: str
        :param src: El registro fuente.
        :type src: str
        :param shamt: La cantidad de bits a desplazar (shift amount).
        :type shamt: str
        """
        dest_reg = dest.lstrip('$').strip(',')
        src_reg = src.lstrip('$').strip(',')
        value = self.get_register_value(src_reg)
        try:
            shift_amount = int(shamt.strip(',')) & 0x1F
            self.set_register_value(dest_reg, value << shift_amount)
        except ValueError:
            print(f"Error: Valor de desplazamiento inválido: {shamt}")

    def and_op(self, dest: str, src1: str, src2: str):
        """
        Implementa la instrucción 'and'.

        Realiza una operación AND bit a bit entre dos registros y
        guarda el resultado.

        :param dest: El registro de destino.
        :type dest: str
        :param src1: El primer registro fuente.
        :type src1: str
        :param src2: El segundo registro fuente.
        :type src2: str
        """
        dest_reg = dest.lstrip('$').strip(',')
        src1_reg = src1.lstrip('$').strip(',')
        src2_reg = src2.lstrip('$').strip(',')
        value1 = self.get_register_value(src1_reg)
        value2 = self.get_register_value(src2_reg)
        self.set_register_value(dest_reg, value1 & value2)

    def or_op(self, dest: str, src1: str, src2: str):
        """
        Implementa la instrucción 'or'.

        Realiza una operación OR bit a bit entre dos registros y
        guarda el resultado.

        :param dest: El registro de destino.
        :type dest: str
        :param src1: El primer registro fuente.
        :type src1: str
        :param src2: El segundo registro fuente.
        :type src2: str
        """
        dest_reg = dest.lstrip('$').strip(',')
        src1_reg = src1.lstrip('$').strip(',')
        src2_reg = src2.lstrip('$').strip(',')
        value1 = self.get_register_value(src1_reg)
        value2 = self.get_register_value(src2_reg)
        self.set_register_value(dest_reg, value1 | value2)

    def nor_op(self, dest: str, src1: str, src2: str):
        """
        Implementa la instrucción 'nor' (not or).

        Realiza una operación OR bit a bit entre dos registros y
        luego invierte el resultado.

        :param dest: El registro de destino.
        :type dest: str
        :param src1: El primer registro fuente.
        :type src1: str
        :param src2: El segundo registro fuente.
        :type src2: str
        """
        dest_reg = dest.lstrip('$').strip(',')
        src1_reg = src1.lstrip('$').strip(',')
        src2_reg = src2.lstrip('$').strip(',')
        value1 = self.get_register_value(src1_reg)
        value2 = self.get_register_value(src2_reg)
        self.set_register_value(dest_reg, ~(value1 | value2))

    def beq(self, rs: str, rt: str, offset: str):
        """
        Implementa la instrucción 'beq' (branch if equal).

        Si el valor de dos registros son iguales, salta a una
        dirección calculada.

        :param rs: El primer registro a comparar.
        :type rs: str
        :param rt: El segundo registro a comparar.
        :type rt: str
        :param offset: El desplazamiento (en words).
        :type offset: str
        """
        rs_reg = rs.lstrip('$').strip(',')
        rt_reg = rt.lstrip('$').strip(',')
        value1 = self.get_register_value(rs_reg)
        value2 = self.get_register_value(rt_reg)
        if value1 == value2:
            try:
                branch_offset = int(offset.strip(','))
                self.instruction_pointer += branch_offset
            except ValueError:
                print(f"Error: Offset de salto inválido: {offset}")

    def bne(self, rs: str, rt: str, offset: str):
        """
        Implementa la instrucción 'bne' (branch if not equal).

        Si el valor de dos registros no son iguales, salta a
        una dirección calculada.

        :param rs: El primer registro a comparar.
        :type rs: str
        :param rt: El segundo registro a comparar.
        :type rt: str
        :param offset: El desplazamiento (en words).
        :type offset: str
        """
        rs_reg = rs.lstrip('$').strip(',')
        rt_reg = rt.lstrip('$').strip(',')
        value1 = self.get_register_value(rs_reg)
        value2 = self.get_register_value(rt_reg)
        if value1 != value2:
            try:
                branch_offset = int(offset.strip(','))
                self.instruction_pointer += branch_offset
            except ValueError:
                print(f"Error: Offset de salto inválido: {offset}")

    def slt(self, dest: str, src1: str, src2: str):
        """
        Implementa la instrucción 'slt' (set less than).

        Establece el registro de destino a 1 si el primer
        registro fuente es menor que el segundo, de lo contrario,
        lo establece a 0.

        :param dest: El registro de destino.
        :type dest: str
        :param src1: El primer registro fuente.
        :type src1: str
        :param src2: El segundo registro fuente.
        :type src2: str
        """
        dest_reg = dest.lstrip('$').strip(',')
        src1_reg = src1.lstrip('$').strip(',')
        src2_reg = src2.lstrip('$').strip(',')
        value1 = self.get_register_value(src1_reg)
        value2 = self.get_register_value(src2_reg)
        if value1 < value2:
            self.set_register_value(dest_reg, 1)
        else:
            self.set_register_value(dest_reg, 0)

    def jump(self, target: str):
        """
        Implementa la instrucción 'j' (jump).

        Salta incondicionalmente a la dirección de la etiqueta especificada.
        De momento, por simplicidad, debe ser el número de línea que requiere
        el jump.

        :param target: La etiqueta de destino del salto.
        :type target: str
        """
        try:
            target_index = int(target)
            if 0 <= target_index < len(self.instructions):
                self.instruction_pointer = target_index
            else:
                print(f"Error: Destino de salto inválido: {target_index}")
        except ValueError:
            print("Error: Destino de salto inválido"
                  f" (no es un número): {target}")


def main(filename: str):
    """
    Función principal para ejecutar la emulación MIPS.

    Crea una instancia del emulador, carga las instrucciones desde el archivo
    especificado, ejecuta las instrucciones y luego imprime el estado de la
    memoria.

    :param filename: Ruta al archivo que contiene el código ensamblador MIPS.
    :type filename: str
    """
    emulator = MIPS_Emulator()
    try:
        emulator.load_instructions(filename)
        emulator.run()
        print("\nEstado final de la memoria:")
        for i, value in enumerate(emulator.memory):
            print(f"memory[{i * 4}] - memory[{i * 4 + 3}]: {value}")
    except FileNotFoundError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python mips_emulator.py <archivo_ensamblador>")
    else:
        assembler_file = sys.argv[1]
        main(assembler_file)
