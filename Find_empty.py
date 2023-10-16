import os

folder_path = r'D:\pycharm\pythonProject\pdf-txt\FR(miner)'


def is_empty(text):
    return len(text)==0

with open('Emptyfile.txt', 'w') as result_file:
    for root, ds, fs in os.walk(folder_path):
        for file_name in fs:
            if file_name.endswith('.txt'):
                with open(os.path.join(root, file_name), 'r', encoding='utf-8') as file:
                    content = file.read(30)
                    if is_empty(content):
                        result_file.write(file_name + '\n')
