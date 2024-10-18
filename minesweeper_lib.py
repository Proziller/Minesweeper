
class minesweeper():
    def __init__(self, difficulty):

        self.map = []

        self.difficulty = 0

        if difficulty == 1:
            self.difficulty = [10,8]
            self.mines = 10
        elif difficulty == 2:
            self.difficulty = [18,14]
            self.mines = 40
        elif difficulty == 3:
            self.difficulty = [24,20]
            self.mines = 99

    def generate(self):
        for i in range(self.difficulty[1]):
            self.map.append([])
            for o in range(self.difficulty[0]):
                self.map.append[i]("▣")
        print(map)
