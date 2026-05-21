class PPU:
    def __init__(self, rom):
        self.rom = rom

        self.vram = [0] * 2048
        self.palette = [0] * 32

        self.control = 0
        self.mask = 0
        self.status = 0

        self.ppu_address = 0
        self.address_latch = 0

    def read(self, address):
        address &= 0x3FFF

        if address == 0x2002:
            value = self.status
            self.address_latch = 0
            return value

        elif address == 0x2007:
            value = self.read_vram(self.ppu_address)
            self.ppu_address = (self.ppu_address + 1) & 0x3FFF
            return value

        return 0

    def write(self, address, value):
        address &= 0x3FFF

        if address == 0x2000:
            self.control = value

        elif address == 0x2001:
            self.mask = value

        elif address == 0x2006:
            if self.address_latch == 0:
                self.ppu_address = value << 8
                self.address_latch = 1
            else:
                self.ppu_address |= value
                self.address_latch = 0

        elif address == 0x2007:
            self.write_vram(self.ppu_address, value)

            increment = 32 if (self.control & 0b00000100) else 1

            self.ppu_address = (
                self.ppu_address + increment
            ) & 0x3FFF

    def read_vram(self, address):
        address &= 0x3FFF

        if address < 0x2000:
            return self.rom.chr_rom[address]

        elif address < 0x3F00:
            return self.vram[address % 2048]

        elif address < 0x4000:
            return self.palette[address % 32]

        return 0

    def write_vram(self, address, value):
        address &= 0x3FFF

        if address < 0x2000:
            pass

        elif address < 0x3F00:
            self.vram[address % 2048] = value

        elif address < 0x4000:
            self.palette[address % 32] = value

    def get_tile_pixel(self, tile, x, y):
        tile_start = tile * 16

        plane0 = self.rom.chr_rom[tile_start + y]
        plane1 = self.rom.chr_rom[tile_start + y + 8]

        bit0 = (plane0 >> (7 - x)) & 1
        bit1 = (plane1 >> (7 - x)) & 1

        return bit0 | (bit1 << 1)

    def render_chr(self, image, scale):
        colors = [
            "#000000",
            "#555555",
            "#AAAAAA",
            "#FFFFFF"
        ]

        for py in range(128):
            row = []

            tile_y = py // 8
            pixel_y = py % 8

            for px in range(128):
                tile_x = px // 8
                pixel_x = px % 8

                tile = tile_y * 16 + tile_x

                color = self.get_tile_pixel(
                    tile,
                    pixel_x,
                    pixel_y
                )

                row.append(colors[color])

            scaled_row = []

            for color in row:
                for i in range(scale):
                    scaled_row.append(color)

            row_data = "{" + " ".join(scaled_row) + "}"

            for sy in range(scale):
                image.put(
                    row_data,
                    to=(0, py * scale + sy)
                )

    def render_nametable(self, image, scale):
        colors = [
            "#000000",
            "#555555",
            "#AAAAAA",
            "#FFFFFF"
        ]

        for tile_y in range(30):
            for tile_x in range(32):
                tile = self.vram[tile_y * 32 + tile_x]

                for y in range(8):
                    row = []

                    for x in range(8):
                        color = self.get_tile_pixel(
                            tile,
                            x,
                            y
                        )

                        row.append(colors[color])

                    scaled_row = []

                    for color in row:
                        for i in range(scale):
                            scaled_row.append(color)

                    row_data = "{" + " ".join(scaled_row) + "}"

                    py = (tile_y * 8 + y) * scale
                    px = tile_x * 8 * scale

                    for sy in range(scale):
                        image.put(
                            row_data,
                            to=(px, py + sy)
                        )