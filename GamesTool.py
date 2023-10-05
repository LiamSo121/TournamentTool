import requests
from Helper import Helper
import re
from Color_Helper import Color_Helper
import time

API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjI3ODY5NjczMywiYWFpIjoxMSwidWlkIjo0MTEzMjIzNSwiaWFkIjoiMjAyMy0wOC0zMVQxMTozMTowNS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTM5OTE1LCJyZ24iOiJ1c2UxIn0.jqoc1M3Sjv0r0Z7m7bt_8gDYZH-MBvQ0FwsNXtBSDGQ"
ENDPOINT = "https://api.monday.com/v2"




class GamesTool:
    def __init__(self):
        self.helper = Helper()
        self.color_helper = Color_Helper()
        self.main_board_id = "3014186450"
        self.main_board_tournament = None
        self.main_board_column_id = None
        self.main_board_columns_names = None
        self.main_Board_items = None
        self.main_board_relevant_items_id = None
        self.selected_tournament = None
        self.selected_round = None

    def get_column_id_from_main_games_board(self):
        board_id = int(self.main_board_id)
        query = f"""
                {{
                    boards(ids: {board_id}) {{
                    columns() {{
                        id
                        title
                    }}
                    }}
                }}
                """
        response = requests.post(ENDPOINT, json={"query": query}, headers={"Authorization": API_KEY})
        data = response.json()
        for column in data['data']['boards'][0]['columns']:
            if column['title'] == "Tournaments":
                self.main_board_column_id = column['id']


    def get_data_from_main_games_board(self):
        query = f"""
            {{
            boards(ids: {self.main_board_id}) {{
                items () {{
                id
                name
                column_values {{
                    id
                    text
                }}
                }}
                columns {{
                id
                title
                }}
            }}
            }}
            """

        response = requests.post(ENDPOINT, json={"query": query}, headers={"Authorization": API_KEY})
        data = response.json()
        columns = data['data']['boards'][0]['columns']
        column_names = {column['id']: column['title'] for column in columns}
        items = data['data']['boards'][0]['items']

        self.main_board_columns_names = column_names
        self.main_Board_items = items


    # In order to find all items from a specific tournament
    # This function assign the selected tournament to self.selected_tournament
    def get_main_board_tournaments(self):
        values_list = []
        tournament_to_decide = []
        for item in self.main_Board_items:
            # item_id = item['id']
            item_columns = item['column_values'] 
            for column in item_columns:
                current_item_id = column['id']
                # column_name = column_names.get(current_item_id, "Unknown Column")
                column_text = column['text']
                if current_item_id == self.main_board_column_id:
                    values_list.append(column_text)
        values_list = list(set(values_list))
        for title in values_list:
            # Find the index of the first space character
            first_space_index = title.find(" ")
            first_hyphen_index = title.find("-")
            # Determine the minimum index among space and hyphen
            if first_space_index != -1 and (first_hyphen_index == -1 or first_space_index < first_hyphen_index):
                first_index = first_space_index
            else:
                first_index = first_hyphen_index if first_hyphen_index != -1 else None
            # Extract the substring from the beginning of the string until the first space or hyphen
            if first_index is not None:
                extracted_text = title[:first_index]
            else:
                extracted_text = title  
            tournament_to_decide.append(extracted_text)
        tournament_to_decide = list(set(tournament_to_decide))
        self.choose_tournament(tournament_to_decide)

    def choose_tournament(self,tournament_to_decide):
        for i,tournament_name in enumerate(tournament_to_decide,start=1):
            print(f"{i}. {tournament_name}")
        while True:
            try:
                user_choice = input("Enter Tournament Name you want to select:")
                user_choice = int(user_choice)
                if 1 <= user_choice <= len(tournament_to_decide):
                    selected_tournament = tournament_to_decide[user_choice - 1]
                    self.color_helper.green_colored_printer(f"You selected: {selected_tournament}")
                    break
                else:
                    self.color_helper.red_colored_printer("Invalid choice. Please enter a valid number.")
            except ValueError:
                self.color_helper.red_colored_printer("Invalid input. Please enter a valid number or 'done' to finish.")
        self.selected_tournament = selected_tournament


    def get_relevant_item_ids_from_main_games_board(self):
        item_ids = []
        for item in self.main_Board_items:
            item_id = item['id']
            item_columns = item['column_values'] 
            for column in item_columns:
                current_item_id = column['id']
                column_name = self.main_board_columns_names.get(current_item_id, "Unknown Column")
                column_text = column['text']
                if column_name == 'Tournaments':
                    if self.selected_tournament in column_text and int(self.helper.target_digit) >= self.get_digits_from_column_name_and_concate(column_text) :
                        item_ids.append(item_id)
        self.main_board_relevant_items_id = item_ids


    def get_digits_from_column_name_and_concate(self,column_text):
        # Use regular expression to find all digits
        digits = re.findall(r'\d+', column_text)
        number = digits[0]
        number = int(number)
        return number

    # For future use on other boards
    def select_tournament_round(self,all_tournament_rounds,selected_tournament):
            relevant_tournament_rounds = []
            for item in all_tournament_rounds:
                if selected_tournament in item:
                    relevant_tournament_rounds.append(item)
            for i,tournament_name in enumerate(relevant_tournament_rounds,start=1):
                print(f"{i}. {tournament_name}")
            while True:
                try:
                    user_choice = input("Enter Tournament Name you want to select:")
                    user_choice = int(user_choice)
                    if 1 <= user_choice <= len(relevant_tournament_rounds):
                        selected_tournament_round = relevant_tournament_rounds[user_choice - 1]
                        self.color_helper.green_colored_printer(f"You selected: {selected_tournament_round}")
                        return user_choice
                    else:
                        self.color_helper.red_colored_printer("Invalid choice. Please enter a valid number.")
                except ValueError:
                    self.color_helper.red_colored_printer("Invalid input. Please enter a valid number or 'done' to finish.")




    def main_games_board(self):
        self.color_helper.red_colored_printer(f"Start process for board:{self.helper.get_board_name(self.main_board_id)}")
        # Get the column id of "Tournaments" in main games board
        # get relevant items id from main board
        self.get_relevant_item_ids_from_main_games_board()
        # prepare items id for fetching
        items_str = self.helper.prepare_items(self.main_board_relevant_items_id)
        self.helper.fetch_relevant_items(items_str,self.main_board_id)
        self.color_helper.green_colored_printer(f"Done process for board:{self.helper.get_board_name(self.main_board_id)} with {self.helper.item_count}")


    def get_tournament(self):
        self.get_column_id_from_main_games_board()
        # fetch data from main games board and store it as variable
        self.get_data_from_main_games_board()
        #get and choose tournament from main game board
        self.get_main_board_tournaments()

    def run_games_tool(self):
        self.helper.games_or_brands = 'games'
        print("Please wait for games script to launch")
        # self.get_tournament()
        self.helper.get_rounds_from_board()
        if self.helper.validate_rounds():
            # check run time of the program
            # start_time = time.time()
            # self.main_games_board()
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
                    self.color_helper.green_colored_printer(f"Done process for board:{self.helper.get_board_name(board_id)} with {self.helper.item_count} relevant items for Round {self.helper.selected_rounds_dict[board_id]}")
        # end_time = time.time()
        # execution_time = end_time- start_time
        # print(execution_time)

