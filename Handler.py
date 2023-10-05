from BrandsTool import BrandsTool
from GamesTool import GamesTool
from Color_Helper import Color_Helper



class Handler:
    def __init__(self) -> None:
        self.brand_tool = BrandsTool()
        self.game_tool = GamesTool()
        self.color_helper = Color_Helper()

    def run(self):
        print("Welcome to the Tournament Tool")
        print("For Brands Enter 1\nFor Games Enter 2\n")
        while True:
            user_choice = str(input("Enter Your choice:"))
            try:
                if user_choice == '1':
                    self.color_helper.green_colored_printer("You have chose Brands Tool")
                    self.brand_tool.run_brands_tool()
                    break
                elif user_choice == '2':
                    self.color_helper.green_colored_printer("You have chose Games Tool")
                    self.game_tool.run_games_tool()
                    break
                else:
                    self.color_helper.red_colored_printer('Answer has to be 1/2!')
            except ValueError:
                self.color_helper.red_colored_printer('Answer has to be 1/2!')



if __name__ == "__main__":
    handler = Handler()
    handler.run()





