class Memory:
    def __init__(self):
        self.memory = []

    def add_memory(self, content, role):
        self.memory.append({"role": role, "content": content})

    def get_memory(self):
        return self.memory[:]
