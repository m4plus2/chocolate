class ROM:
    def __init__(self, path):
        with open(path, "rb") as f:
            self.data = f.read()

        if self.data[0:4] != b"NES\x1a":
            raise Exception("Not a valid NES ROM")

        self.prg_rom_size = self.data[4] * 16384
        self.chr_rom_size = self.data[5] * 8192

        prg_start = 16
        prg_end = prg_start + self.prg_rom_size

        self.prg_rom = self.data[prg_start:prg_end]

        chr_start = prg_end
        chr_end = chr_start + self.chr_rom_size

        self.chr_rom = self.data[chr_start:chr_end]