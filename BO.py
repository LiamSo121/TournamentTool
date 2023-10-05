import json
import pandas as pd
from datetime import datetime
from Color_Helper import Color_Helper



class BackOfficeIntegration:
    def __init__(self) -> None:
        self.items_count = 0
        self.color_helper = Color_Helper()

    def csv_to_dict(self,file_path):
        try:
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path,header=None)
            # Create a list to store the data
            data_list = []

            # Iterate through each row and add it to the list
            for index, row in df.iterrows():
                row = row.to_string()
                row = self.fix_string(row)
                data_list.append(row)
            # Create the final dictionary with the list as a value
            data_dict = {"tournamentBrandListItems": data_list}

            return data_dict

        except Exception as e:
            return {"error": str(e)}
        


    def fix_string(self,string):
        
        self.items_count = self.items_count + 1
        # Split the string by spaces and keep only non-empty parts
        parts = string.split()
        # Join the parts back together with spaces
        cleaned_string = ' '.join(parts[1:])
        cleaned_string = f"{self.items_count};" + cleaned_string

        string_to_insert  = datetime.now()
        string_to_insert = string_to_insert.strftime('%Y-%m-%dT%H:%M:%S')

        if ";;" in cleaned_string:
            parts = cleaned_string.split(";;")
            cleaned_string = f"{parts[0]};{string_to_insert};{parts[1]}"


        return cleaned_string




bo = BackOfficeIntegration()

result = bo.csv_to_dict("Amit's_Board_Brands_ToImport.csv")
if 'error' in result:
    self.
else:
    print(type(result))


result_to_send = json.dumps(result)

