class Block:
    def __init__(self, blockSize):  
        self.content = []
        self.size = blockSize

    def write(self, newContent):
        self.content = newContent

    def read(self):
        return self.content