import requests
import io
import os
from concurrent.futures import ThreadPoolExecutor
from pdfminer.layout import LAParams
import pdfplumber

def get_txt(date, pdf_file, folder_path, word_margin=0.5):
    laparams = LAParams(word_margin=word_margin)
    with pdfplumber.open(pdf_file) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text(laparams=laparams)
    with open(f'{folder_path}/{date}.txt', 'w', encoding='utf-8') as file:
        file.write(text)


def make_folder(year, month, date, pdf_file):
    folder_path = f"D:\\pycharm\\pythonProject\\pdf-txt\\FR\\FR-{year}\\{month}"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    get_txt(date, pdf_file, folder_path)


def process_date(year, month, day):
    if day < 10:
        day_str = f"0{day}"
    else:
        day_str = str(day)

    if month < 10:
        month_str = f"0{month}"
    else:
        month_str = str(month)

    date = f"{year}-{month_str}-{day_str}"
    url = f"https://www.govinfo.gov/content/pkg/FR-{date}/pdf/FR-{date}.pdf"
    response = requests.get(url)
    if response.url == url:
        pdf_file = io.BytesIO(response.content)
        make_folder(year, month_str, date, pdf_file)
        pdf_file.close()
    response.close()


def main():
    with ThreadPoolExecutor() as executor:
        for year in range(1990, 1991):
            for month in range(1, 2):
                days_in_month = 31
                if month == 2:
                    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                        days_in_month = 29
                    else:
                        days_in_month = 28
                elif month in [4, 6, 9, 11]:
                    days_in_month = 30
                executor.map(process_date, [year] * days_in_month, [month] * days_in_month, range(1, days_in_month + 1))


if __name__ == '__main__':
    main()