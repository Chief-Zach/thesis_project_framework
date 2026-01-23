class NoSolutionFound(Exception):
    def __init__(self, filename, extensions):
        self.message = f"No solution found for {filename} with extensions {extensions}"
        super().__init__(self.message)


class MaximumHintsReached(Exception):
    def __init__(self, hints=3):
        self.message = f"No more than {hints} hints can be requested"
        super().__init__(self.message)

class LevelNotFound(Exception):
    def __init__(self, level):
        self.message = f"Level: {level} not found"
        super().__init__(self.message)
