GROUP_SIZE = 3
FIELD_SIZE = GROUP_SIZE**2


class SudokuField:
    def __init__(self, value=None):
        self.domain = list(range(1, FIELD_SIZE+1)) if value is None else [value]
        self.value = value

    def setValue(self, value):
        self.value = value

    def removeFromDomain(self, value):
        self.domain.remove(value)

    def __str__(self):
        return "?" if self.value is None else str(self.value)
