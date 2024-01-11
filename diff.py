import difflib
import os

# for year in range(1936, 1937, 5):
#     file1_path = f'D:\\pycharm\\pythonProject\\pdf-txt\\FR(margin)\\FR-{year}\\12\\{year}-12-31(0.9).txt'
#     file2_path = f'D:\\pycharm\\pythonProject\\pdf-txt\\FR(margin)\\FR-{year}\\12\\{year}-12-31(10.0).txt'
#
#     with open(file1_path, 'r', encoding='utf-8') as file:
#         file1_lines = file.readlines()
#
#     with open(file2_path, 'r', encoding='utf-8') as file:
#         file2_lines = file.readlines()
#
#     diff = difflib.unified_diff(file1_lines, file2_lines, fromfile=file1_path, tofile=file2_path)
#
#     output_path = f'D:\\pycharm\\pythonProject\\pdf-txt\\FR(diff)\\{year}-diff(0.9, 10.0).txt'
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)
#
#     with open(output_path, 'w', encoding='utf-8') as file:
#         file.writelines(diff)

for year in range(1971, 1972, 5):
    file1_path = f'D:\\pycharm\\pythonProject\\pdf-txt\\FR(margin)\\FR-{year}\\12\\{year}-12-29(0.9).txt'
    file2_path = f'D:\\pycharm\\pythonProject\\pdf-txt\\FR(margin)\\FR-{year}\\12\\{year}-12-29(10.0).txt'

    with open(file1_path, 'r', encoding='utf-8') as file:
        file1_lines = file.readlines()

    with open(file2_path, 'r', encoding='utf-8') as file:
        file2_lines = file.readlines()

    diff = difflib.unified_diff(file1_lines, file2_lines, fromfile=file1_path, tofile=file2_path)

    output_path = f'D:\\pycharm\\pythonProject\\pdf-txt\\FR(diff)\\{year}-diff(0.9, 10.0).txt'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as file:
        file.writelines(diff)