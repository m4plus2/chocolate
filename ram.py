class RAM:
    def __init__(self):
        self.data = [0] * 2048  # 2KB

    def read(self, address):
        return self.data[address % 2048]

    def write(self, address, value):
        self.data[address % 2048] = value & 0xFF