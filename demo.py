from pychan import *

print("\nList of all 4chan boards:")
boards = BoardList()
boards.get_boards()
print("/" + "/ /".join(map(str, boards.board_list)) + "/")
