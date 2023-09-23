from colorama import init,Fore,Style
import requests


API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjI3ODY5NjczMywiYWFpIjoxMSwidWlkIjo0MTEzMjIzNSwiaWFkIjoiMjAyMy0wOC0zMVQxMTozMTowNS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTM5OTE1LCJyZ24iOiJ1c2UxIn0.jqoc1M3Sjv0r0Z7m7bt_8gDYZH-MBvQ0FwsNXtBSDGQ"
ENDPOINT = "https://api.monday.com/v2"


init(autoreset=True)


class Helper:
    def __init__(self):
        self.board_ids_dict = {"3029711823": "Amit's_Board","3150598455": "Shir's_Board","4623683288": "Adar's_Board","4623722517": "Dmitry's_Board","4623712864": "Victoria's_Board"}
        self.board_ids_list = ["3029711823","3150598455","4623683288","4623722517","4623712864"]


        # get board name for better user experience
    def get_board_name(self,board_id):
        return self.board_ids_dict[board_id]
    
    def green_colored_printer(self,string):
        print(Fore.GREEN + Style.BRIGHT + string)

    def red_colored_printer(self,string):
        print(Fore.RED + Style.BRIGHT + string)

    def get_board_name(self,board_id):
        return self.board_ids_dict[board_id]
    
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
        response = requests.post(ENDPOINT, json={"query": query}, headers={"Authorization": API_KEY})
        data = response.json()
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
        response = requests.post(ENDPOINT, json={"query": query}, headers={"Authorization": API_KEY})
        data = response.json()
        for item in data['data']['boards'][0]['columns']:
            if item['title'] == "Tournament":
                return item['id']

