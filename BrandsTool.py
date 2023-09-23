import requests
import json
import pandas as pd
import threading
from Helper import Helper
from Shlush import Shlush
import time


#--------------Credentials------------------
API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjI3ODY5NjczMywiYWFpIjoxMSwidWlkIjo0MTEzMjIzNSwiaWFkIjoiMjAyMy0wOC0zMVQxMTozMTowNS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTM5OTE1LCJyZ24iOiJ1c2UxIn0.jqoc1M3Sjv0r0Z7m7bt_8gDYZH-MBvQ0FwsNXtBSDGQ"
ENDPOINT = "https://api.monday.com/v2"

class BrandsTool:
    def __init__(self) -> None:
        self.helper = Helper()
        self.shlush = Shlush()
        self.selected_rounds_dict = {}
        self.items_dict = {}
        self.target_digit = None
        self.item_count = None
        self.stringToShow = None
        self.column_id = None

    def validate_round_number(self):
        self.target_digit = str(input("Enter Round:"))
        while True:
            try:
                answer = input(f'Round Number Selected is: {self.target_digit} ,kindly confirm (y/n):').lower()
                if answer.startswith('y'):
                    return True
                elif answer.startswith('n'):
                    self.target_digit = str(input("Enter Round:"))
                else:
                    self.helper.red_colored_printer('Answer has to be y/n!')
            except ValueError:
                self.helper.red_colored_printer('Answer has to be y/n!')




    # get the rounds that you want to filter on
    def get_rounds_from_board(self):
        self.validate_round_number()
        for board_id in self.helper.board_ids_list:
            self.column_id = self.helper.get_column_tournament_id(board_id)
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
            response = requests.post(ENDPOINT, json={"query": query}, headers={"Authorization": API_KEY})
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
            print(f"Available rounds for {self.helper.get_board_name(board_id)}")
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
                        self.helper.green_colored_printer(f"You selected: {selected_round}")
                        self.selected_rounds_dict[board_id].append(selected_round)
                    else:
                        self.helper.red_colored_printer("Invalid choice. Please enter a valid number.")
                except ValueError:
                    self.helper.red_colored_printer("Invalid input. Please enter a valid number or 'done' to finish.")

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
        response = requests.post(ENDPOINT, json={"query": query}, headers={"Authorization": API_KEY})
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
        # last item is always an example - we remove it
        relevant_items_id.pop()
        return relevant_items_id
        
    # function to fetch items from large boards (we split the board to 5 parts)
    def get_items_from_large_board(self,board_id):
        if self.item_count is not None:
            # Define the number of parts to split into
            num_parts = 5
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
                response_part = requests.post(ENDPOINT, json={"query": query_part}, headers={"Authorization": API_KEY})
                # Parse the API response for the current part
                data_part = response_part.json()
                items = data_part['data']['boards'][0]['items']
                columns = data_part['data']['boards'][0]['columns']
                column_names = {column['id']: column['title'] for column in columns}
                # get all items with matching value on tournament column
                for item in items:
                    item_id = item['id']
                    item_columns = item['column_values']  
                    for column in item_columns:
                        column_name = column_names.get(self.column_id, "Unknown Column")
                        column_text = column['text']
                        if (column_name == "Tournament" and any(column_text == round for round in self.selected_rounds_dict[board_id])):
                            relevant_items_id.append(item_id)
            return relevant_items_id

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
        response = requests.post(ENDPOINT, json={"query": query}, headers={"Authorization": API_KEY})
        data = response.json()
        items = data['data']['boards'][0]['items']
        columns = data['data']['boards'][0]['columns']
        column_names = {column['id']: column['title'] for column in columns}
        # create the excel sheet 
        self.create_excel_sheet(column_names,items,board_id)
        self.shlush.run_shlush_brands_script(board_id)
        self.item_count = len(items)
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
        response = requests.post(ENDPOINT, json={"query": query}, headers={"Authorization": API_KEY})
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
        df.to_excel(f"{self.helper.get_board_name(board_id)}_Output.xlsx",index=False,startrow=2)

    # after all rounds selected, we ask the user to validate the list
    def validate_rounds(self):
        print("Kindly confirm the following Rounds:\n")
        for key in self.selected_rounds_dict.keys():
            self.helper.green_colored_printer(f"Rounds for {self.helper.get_board_name(key)}: {self.selected_rounds_dict[key]}")
        while True:
            try:
                answer = input('Please review the rounds that you have selected and confirm (y/n):').lower()
                if answer.startswith('y'):
                    return True
                elif answer.startswith('n'):
                    exit()
                else:
                    self.helper.red_colored_printer('Answer has to be y/n!')
            except ValueError:
                self.helper.red_colored_printer('Answer has to be y/n!')