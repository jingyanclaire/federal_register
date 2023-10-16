import requests
import PyPDF2
import io
import os
from concurrent.futures import ThreadPoolExecutor


def get_txt(date, html, folder_path):
    pdf_file = io.BytesIO(html.content)
    reader = PyPDF2.PdfReader(pdf_file)
    page = len(reader.pages)

    with open(f'{folder_path}/{date}.txt', 'w', encoding='utf-8') as file:
        for i in range(page):
            file.write(f'{i}\n')
            txt = reader.pages[i].extract_text()
            file.write(txt)


def make_folder(year, month, date, html):
    # need to change the folder path
    folder_path = f"D:\\pycharm\\pythonProject\\pdf-txt\\FR\\FR-{year}\\{month}"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    get_txt(date, html, folder_path)


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
    html = requests.get(url)
    if html.url == url:
        make_folder(year, month_str, date, html)
    html.close()


def main():
    with ThreadPoolExecutor() as executor:
        for year in range(1980, 2001):
            for month in range(1, 13):
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
