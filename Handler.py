import time
from Helper import Helper
from BrandsTool import BrandsTool



class Handler:
    def __init__(self) -> None:
        self.brand_tool = BrandsTool()
        self.helper = Helper()

    def run(self):
        self.brand_tool.get_rounds_from_board()
        if self.brand_tool.validate_rounds():
            # check run time of the program
            start_time = time.time()
            for board_id in self.helper.board_ids_list:
                if self.brand_tool.selected_rounds_dict[board_id] == []:
                    print("No board")
                    continue
                else:
                    self.helper.red_colored_printer(f"Start process for board:{self.helper.get_board_name(board_id)} for Round {self.brand_tool.selected_rounds_dict[board_id]}")
                    self.brand_tool.count_items_from_boards(board_id)
                    if self.brand_tool.item_count > 700:
                        item_ids_with_relevant_round = self.brand_tool.get_items_from_large_board(board_id)
                    else:
                        item_ids_with_relevant_round = self.brand_tool.get_items_from_board(board_id)
                    self.brand_tool.items_dict[board_id] = item_ids_with_relevant_round
                    items_str = self.brand_tool.prepare_items(self.brand_tool.items_dict[board_id])
                    self.brand_tool.fetch_relevant_items(items_str,board_id)
                    self.helper.green_colored_printer(f"Done process for board:{self.helper.get_board_name(board_id)} with {self.brand_tool.item_count} relevant items for Round {self.brand_tool.selected_rounds_dict[board_id]}")


        end_time = time.time()
        execution_time = end_time- start_time
        print(execution_time)


    def on_pushButton_clicked(self):
        print("asdsadsad")





hand = Handler()
hand.run()










