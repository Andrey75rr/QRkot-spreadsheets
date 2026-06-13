import io
from datetime import datetime, timedelta
from typing import List

import xlsxwriter

from app.core.config import settings
from app.core.yandex_client import YandexDiskClient
from app.models.charity_project import CharityProject


def format_time_delta(delta: timedelta) -> str:
    """Форматирует timedelta в читаемую строку."""
    total_seconds = int(delta.total_seconds())
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60

    if days > 0:
        return f"{days} дн. {hours} ч."
    return f"{hours} ч. {minutes} мин."


async def create_simple_report(
        projects: List[CharityProject],
        yandex_client: YandexDiskClient,
) -> str:
    """Создаёт Excel-отчёт по проектам и загружает на Яндекс Диск."""
    now = datetime.now()
    now_str = now.strftime(settings.report_format)
    safe_filename = (
        f"Отчет_{now_str}"
        .replace(':', '-')
        .replace(' ', '_')
        .replace('/', '-')
    )

    upload_url, file_path = await yandex_client.create_excel_file(
        safe_filename, folder="QRKot Reports"
    )

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("Отчет")

    title_format = workbook.add_format({'bold': True, 'font_size': 14})
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#2F75B5',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
    })
    cell_format = workbook.add_format({'border': 1})
    total_format = workbook.add_format({'bold': True, 'border': 1})

    worksheet.merge_range('A1:C1', f"Отчет от {now_str}", title_format)

    headers = ['Название проекта', 'Время сбора', 'Описание']
    for col, header in enumerate(headers):
        worksheet.write(1, col, header, header_format)

    for row, project in enumerate(projects, start=2):
        delta = project.close_date - project.create_date
        worksheet.write(row, 0, project.name, cell_format)
        worksheet.write(row, 1, format_time_delta(delta), cell_format)
        worksheet.write(row, 2, project.description, cell_format)

    total_row = len(projects) + 2
    worksheet.write(total_row, 0, 'Итого проектов:', total_format)
    worksheet.write(total_row, 1, len(projects), total_format)
    worksheet.write(total_row, 2, '', total_format)

    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:C', 40)

    workbook.close()
    output.seek(0)

    await yandex_client.upload_file(upload_url, output.getvalue())
    return await yandex_client.publish_file(file_path)
