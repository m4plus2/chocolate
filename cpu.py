class CPU:
    def __init__(self, rom, ram, ppu):
        self.ppu = ppu
        self.rom = rom
        self.ram = ram

        self.a = 0
        self.x = 0
        self.y = 0

        self.sp = 0xFD

        low = self.read(0xFFFC)
        high = self.read(0xFFFD)

        self.pc = low | (high << 8)

        self.status = 0x24

    def set_zero_and_negative_flags(self, value):
        if value == 0:
            self.status |= 0b00000010
        else:
            self.status &= 0b11111101

        if value & 0x80:
            self.status |= 0b10000000
        else:
            self.status &= 0b01111111

    def push(self, value):
        self.write(0x100 + self.sp, value)
        self.sp = (self.sp - 1) & 0xFF

    def pop(self):
        self.sp = (self.sp + 1) & 0xFF
        return self.read(0x100 + self.sp)

    def read(self, address):
        if address < 0x2000:
            return self.ram.read(address)

        if 0x2000 <= address < 0x4000:
            return self.ppu.read(address)

        if address >= 0x8000:
            addr = address - 0x8000

            if len(self.rom.prg_rom) == 16384:
                addr %= 16384

            return self.rom.prg_rom[addr]

        return 0

    def write(self, address, value):
        if address < 0x2000:
            self.ram.write(address, value)

        elif 0x2000 <= address < 0x4000:
            self.ppu.write(address, value)

    def step(self):
        opcode = self.read(self.pc)
        self.pc += 1

        if opcode == 0xA9:
            value = self.read(self.pc)
            self.pc += 1

            self.a = value
            self.set_zero_and_negative_flags(self.a)

        elif opcode == 0xA2:
            value = self.read(self.pc)
            self.pc += 1

            self.x = value
            self.set_zero_and_negative_flags(self.x)

        elif opcode == 0xA0:
            value = self.read(self.pc)
            self.pc += 1

            self.y = value
            self.set_zero_and_negative_flags(self.y)

        elif opcode == 0x8D:
            low = self.read(self.pc)
            self.pc += 1

            high = self.read(self.pc)
            self.pc += 1

            addr = low | (high << 8)

            self.write(addr, self.a)

        elif opcode == 0xE8:
            self.x = (self.x + 1) & 0xFF
            self.set_zero_and_negative_flags(self.x)

        elif opcode == 0x4C:
            low = self.read(self.pc)
            self.pc += 1

            high = self.read(self.pc)
            self.pc += 1

            self.pc = low | (high << 8)

        elif opcode == 0x20:
            low = self.read(self.pc)
            self.pc += 1

            high = self.read(self.pc)
            self.pc += 1

            return_addr = self.pc - 1

            self.push((return_addr >> 8) & 0xFF)
            self.push(return_addr & 0xFF)

            self.pc = low | (high << 8)

        elif opcode == 0x60:
            low = self.pop()
            high = self.pop()

            self.pc = ((high << 8) | low) + 1

        elif opcode == 0xD0:
            offset = self.read(self.pc)
            self.pc += 1

            if not (self.status & 0b00000010):
                if offset < 0x80:
                    self.pc += offset
                else:
                    self.pc += offset - 256

        elif opcode == 0xA5:
            addr = self.read(self.pc)
            self.pc += 1

            self.a = self.read(addr)
            self.set_zero_and_negative_flags(self.a)

        elif opcode == 0xAD:
            low = self.read(self.pc)
            self.pc += 1

            high = self.read(self.pc)
            self.pc += 1

            addr = low | (high << 8)

            self.a = self.read(addr)
            self.set_zero_and_negative_flags(self.a)

        elif opcode == 0x85:
            addr = self.read(self.pc)
            self.pc += 1

            self.write(addr, self.a)

        elif opcode == 0x9D:
            low = self.read(self.pc)
            self.pc += 1

            high = self.read(self.pc)
            self.pc += 1

            addr = ((high << 8) | low) + self.x

            self.write(addr & 0xFFFF, self.a)

        elif opcode == 0xA6:
            addr = self.read(self.pc)
            self.pc += 1

            self.x = self.read(addr)
            self.set_zero_and_negative_flags(self.x)

        elif opcode == 0x69:
            value = self.read(self.pc)
            self.pc += 1

            result = self.a + value

            if result > 0xFF:
                self.status |= 0b00000001
            else:
                self.status &= 0b11111110

            self.a = result & 0xFF
            self.set_zero_and_negative_flags(self.a)

        elif opcode == 0xC9:
            value = self.read(self.pc)
            self.pc += 1

            result = (self.a - value) & 0xFF

            if self.a >= value:
                self.status |= 0b00000001
            else:
                self.status &= 0b11111110

            self.set_zero_and_negative_flags(result)

        elif opcode == 0xF0:
            offset = self.read(self.pc)
            self.pc += 1

            if self.status & 0b00000010:
                if offset < 0x80:
                    self.pc += offset
                else:
                    self.pc += offset - 256

        elif opcode == 0x10:
            offset = self.read(self.pc)
            self.pc += 1

            if not (self.status & 0b10000000):
                if offset < 0x80:
                    self.pc += offset
                else:
                    self.pc += offset - 256

        elif opcode == 0x18:
            self.status &= 0b11111110

        elif opcode == 0x78:
            self.status |= 0b00000100

        elif opcode == 0xD8:
            self.status &= 0b11110111
            
        elif opcode == 0x9A:
            self.sp = self.x

        else:
            print(f"Unknown opcode: {hex(opcode)} at {hex(self.pc - 1)}")