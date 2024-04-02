import math
from simpleai.search import SearchProblem, astar
import numpy as np
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import time 

# Define cost of moving around the map
cost_regular = 1.0
cost_diagonal = 1.7

# Create the cost dictionary
COSTS = {
    "up": cost_regular,
    "down": cost_regular,
    "left": cost_regular,
    "right": cost_regular,
    "up left": cost_diagonal,
    "up right": cost_diagonal,
    "down left": cost_diagonal,
    "down right": cost_diagonal,
}

# Define the map
MAP = """
##############################
#         #              #   #
# ####    ########       #   #
#    #    #              #   #
#    ###     #####  ######   #
#      #   ###   #           #
#      #     #   #  #  #   ###
#     #####    #    #  #     #
#              #       #     #
##############################
"""

# Convert map to a list
MAP = [list(x) for x in MAP.split("\n") if x]

M = 10
N = 30
W = 21
mau_xanh = np.zeros((W,W,3), np.uint8) + (np.uint8(255), np.uint8(0), np.uint8(0))
mau_trang = np.zeros((W,W,3), np.uint8) + (np.uint8(255), np.uint8(255), np.uint8(255))
image = np.ones((M*W, N*W, 3), np.uint8)*255 

for x in range(0, M):
    for y in range(0, N):
        if MAP[x][y] == '#':
            image[x*W:(x+1)*W, y*W:(y+1)*W] = mau_xanh
        elif MAP[x][y] == ' ':
            image[x*W:(x+1)*W, y*W:(y+1)*W] = mau_trang

color_coverted = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
pil_image = Image.fromarray(color_coverted)

class MazeSolver(SearchProblem):
    def __init__(self, board):
        self.board = board
        self.goal = (0, 0)

        for y in range(len(self.board)):
            for x in range(len(self.board[y])):
                if self.board[y][x].lower() == "o":
                    self.initial = (x, y)
                elif self.board[y][x].lower() == "x":
                    self.goal = (x, y)

        super(MazeSolver, self).__init__(initial_state=self.initial)

    def actions(self, state):
        actions = []
        for action in COSTS.keys():
            newx, newy = self.result(state, action)
            if self.board[newy][newx] != "#":
                actions.append(action)

        return actions

    def result(self, state, action):
        x, y = state

        if action.count("up"):
            y -= 1
        if action.count("down"):
            y += 1
        if action.count("left"):
            x -= 1
        if action.count("right"):
            x += 1

        new_state = (x, y)

        return new_state

    def is_goal(self, state):
        return state == self.goal

    def cost(self, state, action, state2):
        return COSTS[action]

    def heuristic(self, state):
        x, y = state
        gx, gy = self.goal
        return math.sqrt((x - gx) ** 2 + (y - gy) ** 2)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.dem = 0
        self.reset_done = False  # Thêm biến cờ để theo dõi trạng thái reset
        self.title('Tìm đường mê cung')
        self.cvs_me_cung = tk.Canvas(self, width = N*W, height = M*W,
                                relief = tk.SUNKEN, border = 1)

        self.image_tk = ImageTk.PhotoImage(pil_image)
        self.cvs_me_cung.create_image(0, 0, anchor = tk.NW, image = self.image_tk)
        self.cvs_me_cung.bind("<Button-1>",self.xu_ly_mouse)


        btn_start = tk.Button(self,text='Start',width=7,command=self.btn_start_click)
        btn_reset = tk.Button(self,text='Reset',width=7,command=self.btn_reset_click)

        self.cvs_me_cung.grid(row = 0, column = 0, padx = 5, pady = 5)
        btn_start.grid(row = 0, column= 1, padx = 5, pady= 5, sticky=tk.N)
        btn_reset.grid(row = 0, column= 2, padx = 5, pady= 5, sticky=tk.N)

    def xu_ly_mouse(self, event):
        global MAP
        if self.dem == 0:
            px = event.x
            py = event.y
            x = px // W
            y = py // W
            if MAP[y][x] != '#':  # Kiểm tra xem vị trí được click có phải là một phần tường không
                MAP = [list(row) for row in MAP]  # Chuyển đổi mê cung thành danh sách các danh sách ký tự
                MAP[y][x] = 'o'
                self.cvs_me_cung.create_oval(x * W + 2, y * W + 2, (x + 1) * W - 2, (y + 1) * W - 2, outline='#FF0000',
                                            fill='#FF0000')
                self.dem += 1
        elif self.dem == 1:
            px = event.x
            py = event.y
            x = px // W
            y = py // W
            if MAP[y][x] != '#':  # Kiểm tra xem vị trí được click có phải là một phần tường không
                MAP = [list(row) for row in MAP]  # Chuyển đổi mê cung thành danh sách các danh sách ký tự
                MAP[y][x] = 'x'
                self.cvs_me_cung.create_rectangle(x * W + 2, y * W + 2, (x + 1) * W - 2, (y + 1) * W - 2,
                                                outline='#ff69b4', fill='#ff69b4')
                self.dem += 1




    def btn_start_click(self):
        self.reset_done = False  # Đánh dấu là chưa reset
        problem = MazeSolver(MAP)
        result = astar(problem, graph_search=True)
        path = [x[1] for x in result.path()]
        for i in range(1, len(path)):
            x = path[i][0]
            y = path[i][1]
            self.cvs_me_cung.create_rectangle(x*W+2,y*W+2, (x+1)*W-2,(y+1)*W-2, fill= '#ff69b4',outline='#ff69b4')
            time.sleep(0.5)
            self.cvs_me_cung.update()

    def btn_reset_click(self):
        self.cvs_me_cung.delete("all")
        self.cvs_me_cung.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
        global MAP
        MAP = [
            "##############################",
            "#         #              #   #",
            "# ####    ########       #   #",
            "#    #    #              #   #",
            "#    ###     #####  ######   #",
            "#      #   ###   #           #",
            "#      #     #   #  #  #   ###",
            "#     #####    #    #  #     #",
            "#              #       #     #",
            "##############################"
        ]
        self.dem = 0
        self.reset_done = True  # Đánh dấu là đã reset



if __name__ == "__main__":
    app = App()
    app.mainloop()
