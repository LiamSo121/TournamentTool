from Color_Helper import Color_Helper
from Helper import Helper
from Shlush import Shlush
from BO import BackOfficeIntegration
import time


class BrandsTool:
    def __init__(self) -> None:
        self.color_helper = Color_Helper()
        self.bo = BackOfficeIntegration()
        self.helper = Helper()
        self.shlush = Shlush()
        self.stringToShow = None
        self.column_id = None






    def run_brands_tool(self):
        self.helper.games_or_brands = 'brands'
        self.helper.get_rounds_from_board()
        if self.helper.validate_rounds():
            for board_id in self.helper.board_ids_list:
                if self.helper.selected_rounds_dict[board_id] == []:
                    print("No board")
                    continue
                else:
                    self.color_helper.blue_colored_printer(f"Start process for board:{self.helper.get_board_name(board_id)} for Round {self.helper.selected_rounds_dict[board_id]}")
                    self.helper.count_items_from_boards(board_id)
                    item_ids_with_relevant_round = self.helper.get_items_from_large_board(board_id)
                    self.helper.items_dict[board_id] = item_ids_with_relevant_round
                    items_str = self.helper.prepare_items(self.helper.items_dict[board_id])
                    self.helper.fetch_relevant_items(items_str,board_id)
                    self.bo.csv_to_dict(f"{self.helper.get_board_name(board_id)}_Brands_ToImport.csv")
                    self.color_helper.green_colored_printer(f"Done process for board:{self.helper.get_board_name(board_id)} with {self.helper.item_count} relevant items for Round {self.helper.selected_rounds_dict[board_id]}")