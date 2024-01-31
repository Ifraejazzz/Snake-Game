import tkinter as tk
from random import randint
from PIL import Image, ImageTk

MOVE_INCREMENT = 20
MOVES_PER_SECOND = 15
GAME_SPEED = 1000 // MOVES_PER_SECOND


class Snake(tk.Canvas):
    def __init__(self):
        super().__init__(
            width=800, height=620,  # Increase the width to 800
            background="black", highlightthickness=0
        )

        self.human_snake_positions = [(100, 100), (80, 100), (60, 100)]
        self.computer_snake_positions = [(500, 500), (520, 500), (540, 500)]

        self.food_position = self.set_new_food_position()

        self.human_direction = "Right"
        self.computer_direction = "Left"

        self.human_score = len(self.human_snake_positions)
        self.computer_score = len(self.computer_snake_positions)

        self.load_assets()
        self.create_objects()

        self.bind_all("<Key>", self.on_key_press)

        self.pack()

        self.after(GAME_SPEED, self.perform_actions)

    def load_assets(self):
        try:
            self.snake_body_image = Image.open("./snake.png")
            self.snake_body = ImageTk.PhotoImage(self.snake_body_image)

            self.food_image = Image.open("./food.png")
            self.food = ImageTk.PhotoImage(self.food_image)
        except IOError as error:
            root.destroy()
            raise

    def create_objects(self):
        self.create_text(
            70, 12, text=f"Human Length: {self.human_score}", tag="human_score", fill="#fff", font=10
        )
        self.create_text(
            530, 12, text=f"Computer Length: {self.computer_score}", tag="computer_score", fill="#fff", font=10
        )

        for x_position, y_position in self.human_snake_positions:
            self.create_image(
                x_position, y_position, image=self.snake_body, tag="human_snake"
            )

        for x_position, y_position in self.computer_snake_positions:
            self.create_image(
                x_position, y_position, image=self.snake_body, tag="computer_snake"
            )

        self.food_id = self.create_image(*self.food_position, image=self.food, tag="food")
        self.create_rectangle(7, 27, 793, 613, outline="#525d69")  # Increase the right boundary to 793

    def check_collisions(self, snake_positions):
        head_x_position, head_y_position = snake_positions[0]

        return (
            head_y_position < 20
            or head_y_position >= 620
            or head_x_position < 0
            or head_x_position >= 800  # Adjust the right boundary to 800
            or (head_x_position, head_y_position) in snake_positions[1:]
        )

    def check_food_collision(self, snake_positions, score_tag):
        if snake_positions[0] == self.food_position:
            snake_positions.append(snake_positions[-1])

            if score_tag == "human_score":
                self.human_score = len(snake_positions)
                self.create_image(
                    *snake_positions[-1], image=self.snake_body, tag="human_snake"
                )
            else:
                self.computer_score = len(snake_positions)
                self.create_image(
                    *snake_positions[-1], image=self.snake_body, tag="computer_snake"
                )

            self.food_position = self.set_new_food_position()
            self.coords(self.food_id, *self.food_position)

            self.update_score_text("human_score", self.human_score)
            self.update_score_text("computer_score", self.computer_score)

    def update_score_text(self, score_tag, score):
        score_text = f"{score_tag.capitalize()} Length: {score}"
        self.itemconfigure(score_tag, text=score_text)

    def end_game(self):
        self.delete(tk.ALL)
        winner = "Human" if self.human_score > self.computer_score else "Computer"
        self.create_text(
            self.winfo_width() / 2,
            self.winfo_height() / 2,
            text=f"Game over! {winner} wins with a length of {max(self.human_score, self.computer_score)}!",
            fill="#fff",
            font=14
        )

    def move_snake(self, snake_positions, direction, tag):
        head_x_position, head_y_position = snake_positions[0]

        if direction == "Left":
            new_head_position = (head_x_position - MOVE_INCREMENT, head_y_position)
            if new_head_position[0] < 0:
                new_head_position = (self.winfo_width() - MOVE_INCREMENT, head_y_position)
        elif direction == "Right":
            new_head_position = (head_x_position + MOVE_INCREMENT, head_y_position)
            if new_head_position[0] >= self.winfo_width():
                new_head_position = (0, head_y_position)
        elif direction == "Down":
            new_head_position = (head_x_position, head_y_position + MOVE_INCREMENT)
            if new_head_position[1] >= self.winfo_height():
                new_head_position = (head_x_position, 20)
        elif direction == "Up":
            new_head_position = (head_x_position, head_y_position - MOVE_INCREMENT)
            if new_head_position[1] < 20:
                new_head_position = (head_x_position, self.winfo_height() - MOVE_INCREMENT)

        snake_positions = [new_head_position] + snake_positions[:-1]

        for segment, position in zip(self.find_withtag(tag), snake_positions):
            self.coords(segment, position)

        return snake_positions

    def on_key_press(self, e):
        new_direction = e.keysym

        all_directions = ("Up", "Down", "Left", "Right")
        opposites = ({"Up", "Down"}, {"Left", "Right"})

        if (
            new_direction in all_directions
            and {new_direction, self.human_direction} not in opposites
        ):
            self.human_direction = new_direction

    def perform_actions(self):
        if self.check_collisions(self.human_snake_positions) or self.check_collisions(self.computer_snake_positions):
            self.end_game()
            return  # Exit the function to stop further actions after game over

        self.check_food_collision(self.human_snake_positions, "human_score")
        self.check_food_collision(self.computer_snake_positions, "computer_score")

        self.human_snake_positions = self.move_snake(self.human_snake_positions, self.human_direction, "human_snake")

        # AI Snake (Computer)
        self.computer_snake_positions = self.move_ai_snake(self.computer_snake_positions)

        self.after(GAME_SPEED, self.perform_actions)

    def move_ai_snake(self, snake_positions):
        head_x, head_y = snake_positions[0]
        food_x, food_y = self.food_position

        if food_x > head_x:
            return self.move_snake(snake_positions, "Right", "computer_snake")
        elif food_x < head_x:
            return self.move_snake(snake_positions, "Left", "computer_snake")
        elif food_y > head_y:
            return self.move_snake(snake_positions, "Down", "computer_snake")
        elif food_y < head_y:
            return self.move_snake(snake_positions, "Up", "computer_snake")

        return snake_positions

    def set_new_food_position(self):
        while True:
            x_position = randint(1, 39) * MOVE_INCREMENT  # Adjust the x-position range to fit the wider canvas
            y_position = randint(3, 30) * MOVE_INCREMENT
            food_position = (x_position, y_position)

            if (
                food_position not in self.human_snake_positions
                and food_position not in self.computer_snake_positions
            ):
                return food_position


root = tk.Tk()
root.title("Snake")
root.resizable(False, False)
root.tk.call("tk", "scaling", 4.0)

board = Snake()

root.mainloop()
