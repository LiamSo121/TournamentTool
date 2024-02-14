import requests
import json
import pandas as pd
from Shlush import Shlush
from Color_Helper import Color_Helper
from dotenv import load_dotenv
import os

class Helper:
    load_dotenv()
    def __init__(self):
            self.api_key = os.getenv("API_KEY")
            self.endpoint = os.getenv("ENDPOINT")
            self.parts_num = int(os.getenv("PARTS_NUM"))
            self.color_helper = Color_Helper()
            self.shlush = Shlush()
            self.board_ids_dict = {"3029711823": "Amit's_Board","3150598455": "Shir's_Board","4623683288": "Adar's_Board","4623722517": "Dmitry's_Board","4623712864": "Victoria's_Board","3014186450":"Main_Games_Board"}
            self.board_ids_list = ["3029711823","3150598455","4623683288","4623722517","4623712864"]
            self.target_digit = None
            self.item_count = None
            self.column_id = None
            self.items_dict = {}
            self.selected_rounds_dict = {}
            self.games_or_brands = None

        # get board name for better user experience
    def get_board_name(self,board_id):
        return self.board_ids_dict[board_id]
    
    def remove_excel_from_folder(self,excel_name):
        if os.path.exists(excel_name):
            os.remove(excel_name)
            print(f"{excel_name} has been removed.")
        else:
            print(f"{excel_name} does not exist.")
    

    def get_column_tournament_id(self,board_id):
        board_id = int(board_id)
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
        response = requests.post(self.endpoint, json={"query": query}, headers={"Authorization": self.api_key})
        data = response.json()
        print(data)
        for item in data['data']['boards'][0]['columns']:
            if item['title'] == "Tournament":
                return item['id']

    def get_column_id_from_main_games_board(self,board_id):
        board_id = int(board_id)
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
        response = requests.post(self.endpoint, json={"query": query}, headers={"Authorization": self.api_key})
        data = response.json()
        for item in data['data']['boards'][0]['columns']:
            if item['title'] == "Tournament":
                return item['id']

    def validate_round_number(self):
        self.target_digit = str(input("Enter Round:"))
        while True:
            try:
                answer = input(f'Round Number Selected is: {self.target_digit} ,kindly confirm (y/n):').lower()
                if answer.startswith('y'):
                    break
                elif answer.startswith('n'):
                    self.target_digit = str(input("Enter Round:"))
                else:
                    self.color_helper.red_colored_printer('Answer has to be y/n!')
            except ValueError:
                self.color_helper.red_colored_printer('Answer has to be y/n!')


    # after all rounds selected, we ask the user to validate the list
    def validate_rounds(self):
        print("Kindly confirm the following Rounds:")
        for key in self.selected_rounds_dict.keys():
            self.color_helper.green_colored_printer(f"Rounds for {self.get_board_name(key)}: {self.selected_rounds_dict[key]}")
        while True:
            try:
                answer = input('Please review the rounds that you have selected and confirm (y/n):').lower()
                if answer.startswith('y'):
                    return True
                elif answer.startswith('n'):
                    exit()
                else:
                    self.color_helper.red_colored_printer('Answer has to be y/n!')
            except ValueError:
                self.color_helper.red_colored_printer('Answer has to be y/n!')
    # get the rounds that you want to filter on
    def get_rounds_from_board(self):
        # self.validate_round_number()
        for board_id in self.board_ids_list:
            self.column_id = self.get_column_tournament_id(board_id)
            query = f"""
                        {{
                            boards(ids: {board_id}) {{
                            columns(ids: {self.column_id}) {{
                                settings_str
                            }}
                            }}
                        }}
                        """
            #get the response and parse it
            response = requests.post(self.endpoint, json={"query": query}, headers={"Authorization": self.api_key})
            data = response.json()
            # Extract the list of label names
            settings_str = data['data']['boards'][0]['columns'][0]['settings_str']
            labels = json.loads(settings_str)["labels"]
            label_names = [label["name"] for label in labels]
            # Use list comprehension to filter the list
            label_names = [item for item in label_names if self.target_digit in item and any(char.isdigit() for char in item)]
            #create a key to and a list as value and append each selected round
            self.selected_rounds_dict[board_id] = []
            # Create a menu to select a round
            print(f"Available rounds for {self.get_board_name(board_id)}")
            for i, round_name in enumerate(label_names, start=1):
                print(f"{i}. {round_name}")
            while True:
                try:
                    user_choice = input("Enter the number of the round you want to select (or 'done' to finish): ")
                    if user_choice.lower() == 'done':
                        print("Moving to the board")
                        break
                    user_choice = int(user_choice)
                    if 1 <= user_choice <= len(label_names):
                        selected_round = label_names[user_choice - 1]
                        self.color_helper.green_colored_printer(f"You selected: {selected_round}")
                        self.selected_rounds_dict[board_id].append(selected_round)
                    else:
                        self.color_helper.red_colored_printer("Invalid choice. Please enter a valid number.")
                except ValueError:
                    self.color_helper.red_colored_printer("Invalid input. Please enter a valid number or 'done' to finish.")
    

    # function to count items number in order to determine which function will query the board
    def count_items_from_boards(self,board_id):
        query = f"""
        {{
            boards(ids: {board_id}) {{
                items_count
            }}
        }}
        """
        # Make the API request to get the item count
        response = requests.post(self.endpoint, json={"query": query}, headers={"Authorization": self.api_key})
        # Parse the API response
        data = response.json()
        # Extract the item count
        item_count = data.get("data", {}).get("boards", [])[0].get("items_count", None)
        self.item_count = item_count



        # create an excel sheet that match the form of a exported monday board with compability to shlush script
    def create_excel_sheet(self,column_names,items,board_id):
        # get a list of all the columns
        column_names_list = list(column_names.values())
        dict_to_excel = {}
        for column_name in column_names_list:
            dict_to_excel[column_name] = []
        # iterate over the relevant items and append to matching list
        for item in items:
                item_columns = item['column_values']
                dict_to_excel['Name'].append(item['name'])
                for column in item_columns:
                    current_column_id = column['id']
                    column_name = column_names.get(current_column_id, "Unknown Column")
                    column_text = column['text']
                    dict_to_excel[column_name].append(column_text)
        # create a df and add the values in the matching position 
        df = pd.DataFrame(columns=column_names_list)
        if len(df.columns) == len(column_names_list):
            for column in df.columns:
                df[column] = dict_to_excel[column]
        if self.games_or_brands == "brands":
            df.to_excel(f"{self.get_board_name(board_id)}_Brands_Output.xlsx",index=False,startrow=2)
        else:
            df.to_excel(f"{self.get_board_name(board_id)}_Games_Output.xlsx",index=False,startrow=2)



    # function to fetch all items from a board
    def get_items_from_board(self,board_id):
        # build query
        query = f"""
        {{
        boards(ids: {board_id}) {{
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
        # get and parse response
        response = requests.post(self.endpoint, json={"query": query}, headers={"Authorization": self.api_key})
        data = response.json()
        items = data['data']['boards'][0]['items']
        columns = data['data']['boards'][0]['columns']
        column_names = {column['id']: column['title'] for column in columns}
        relevant_items_id = []
        # append item id which the tournament column value equals the selected round
        for item in items:
            item_id = item['id']
            item_columns = item['column_values']  
            for column in item_columns:
                column_name = column_names.get(self.column_id, "Unknown Column")
                column_text = column['text']
                if (column_name == "Tournament" and any(column_text == round for round in self.selected_rounds_dict[board_id])):
                    relevant_items_id.append(item_id)
        if relevant_items_id == []:
            self.get_items_from_board(board_id)
        # last item is always an example - we remove it
        relevant_items_id.pop()
        return relevant_items_id
    # function to fetch items from large boards (we split the board to 5 parts)
    def get_items_from_large_board(self,board_id):
        try:
            # Define the number of parts to split into
            num_parts = self.parts_num
            relevant_items_id = []
            # Calculate the number of items per part
            items_per_part = self.item_count // num_parts
            # Loop to retrieve items for each part
            for part in range(num_parts):
                # Calculate the range for the current part
                start_index = part * items_per_part
                end_index = (part + 1) * items_per_part if part < num_parts - 1 else self.item_count
                # Calculate page number and page size for the current request
                page_size = end_index - start_index
                page_number = start_index // page_size + 1
                # Construct the GraphQL query for the current part
                query_part = f"""
                {{
                    boards(ids: {board_id}) {{
                        items (limit: {page_size}, page: {page_number}) {{
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
                # Make the API request for the current part
                response_part = requests.post(self.endpoint, json={"query": query_part}, headers={"Authorization": self.api_key})
                # Parse the API response for the current part
                data_part = response_part.json()
                items = data_part['data']['boards'][0]['items']
                columns = data_part['data']['boards'][0]['columns']
                column_names = {column['id']: column['title'] for column in columns}
                # get all items with matching value on tournament column
                for item in items:
                    item_id = item['id']
                    # if page_number == (num_parts - 1):
                    #     print(f"last part item id: {item_id}")
                    item_columns = item['column_values']  
                    for column in item_columns:
                        column_name = column_names.get(self.column_id, "Unknown Column")
                        column_text = column['text']
                        if (column_name == "Tournament" and any(column_text == round for round in self.selected_rounds_dict[board_id])):
                            relevant_items_id.append(item_id)
            return relevant_items_id
        except Exception as e:
            print(e)
            return self.get_items_from_large_board(board_id)
            

    # re organize the items list in order to fetch the rows of the items
    def prepare_items(self,relevant_items_id):
        int_televant_items_id = [int(item) for item in relevant_items_id]
        item_ids_str = ", ".join([str(item_id) for item_id in int_televant_items_id])
        return item_ids_str

    # fetch information of all the relevant items
    def fetch_relevant_items(self,item_ids_str,board_id):
        query = f"""
        {{
            boards(ids: {board_id}) {{
            items(ids: [{item_ids_str}]) {{
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
        # get and parse the request
        response = requests.post(self.endpoint, json={"query": query}, headers={"Authorization": self.api_key})
        data = response.json()
        items = data['data']['boards'][0]['items']
        columns = data['data']['boards'][0]['columns']
        column_names = {column['id']: column['title'] for column in columns}
        # create the excel sheet 
        self.create_excel_sheet(column_names,items,board_id)
        if self.games_or_brands == 'brands':
            print(f"Shlush Brands Script has started board {self.get_board_name(board_id)}")
            self.shlush.shlush_brands_func(self.get_board_name(board_id))
            self.shlush.shlush_to_csv(self.get_board_name(board_id))
            print(f"Shlush Brands Script has finished board {self.get_board_name(board_id)}")
            self.remove_excel_from_folder(f"{self.get_board_name(board_id)}_Brands_Output.xlsx")

        else:
            print(f"Shlush Games Script has started board {self.get_board_name(board_id)}")
            self.shlush.shlush_games_func(self.get_board_name(board_id))
            print(f"Shlush Games Script has finished board {self.get_board_name(board_id)}")
            self.remove_excel_from_folder(f"{self.get_board_name(board_id)}_Games_Output.xlsx")
        
        self.item_count = len(items)