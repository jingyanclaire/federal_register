import pandas as pd
import re
import csv

def create_dataframe():
    data = {
        'department': [],
        'office': [],
        'codification': [],
        'intro': [],
        'agency': [],
        'action': []
    }
    df = pd.DataFrame(data)
    print(df)

def separate_by_page_number(file_path):
    pattern = r'^(.*)\s\/'
    text = re.match(pattern, page_line)
    split_text = text.split('/')
    data = split_text[-2].strip()
    if match:
        return data
    else:
        return None
    df = pd.read_csv(file_path, names=['Text'], sep='\n')
    df['data'] = df['Text'].str.extract(r'data(\d+)')
    df['Part'] = (df['data'] != df['data'].shift()).cumsum()
    result = df.groupby('Part')['Text'].apply('\n'.join).reset_index(drop=True)

def separate_lines(text):
    lines = text.split('\n')
    result = []
    current_part = []
    for line in lines:
        if line.startswith('[FR'):
            if current_part:
                result.append(current_part)
                current_part = []
        current_part.append(line)
        return result


def match_content(text, csv_file):
    matched_rows = []
    with open('agency_names.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Check if the text is found in any column of the current row
            if any(text.lower() in column.lower() for column in row):
                print(text)
            else:
                print("No agency found")

