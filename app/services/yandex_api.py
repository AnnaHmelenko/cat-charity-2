import io
from datetime import datetime, timedelta

import xlsxwriter

from app.core.config import settings
from app.core.constants import (
    CELL_FORMAT,
    HEADER_FORMAT,
    TABLE_HEADERS,
    TITLE_FORMAT,
    TOTAL_FORMAT,
)
from app.core.yandex_client import YandexDiskClient
from app.models.charity_project import CharityProject


def format_time_delta(delta: timedelta) -> str:
    total_minutes = int(delta.total_seconds() // 60)
    days, remainder = divmod(total_minutes, 24 * 60)
    hours, minutes = divmod(remainder, 60)
    if days:
        return f"{days} дн. {hours} ч."
    return f"{hours} ч. {minutes} мин."


async def create_simple_report(
    projects: list[CharityProject],
    yandex_client: YandexDiskClient,
) -> str:
    now = datetime.now()
    filename = f"QRKot_report_{now.strftime(settings.report_format)}.xlsx"

    async with yandex_client as client:
        upload_url, path = await client.create_excel_file(filename)

        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer, {"in_memory": True})
        worksheet = workbook.add_worksheet("Отчёт")

        title_format = workbook.add_format(TITLE_FORMAT)
        header_format = workbook.add_format(HEADER_FORMAT)
        cell_format = workbook.add_format(CELL_FORMAT)
        total_format = workbook.add_format(TOTAL_FORMAT)

        worksheet.set_column("A:A", 30)
        worksheet.set_column("B:B", 20)
        worksheet.set_column("C:C", 40)

        worksheet.write(
            0, 0,
            f'Отчёт от {now.strftime("%d.%m.%Y %H:%M:%S")}',
            title_format,
        )

        for column, header in enumerate(TABLE_HEADERS):
            worksheet.write(1, column, header, header_format)

        row = 2
        for project in projects:
            collection_time = project.close_date - project.create_date
            worksheet.write(row, 0, project.name, cell_format)
            worksheet.write(
                row, 1, format_time_delta(collection_time), cell_format
            )
            worksheet.write(row, 2, project.description, cell_format)
            row += 1

        worksheet.write(
            row, 0, f"Всего проектов: {len(projects)}", total_format
        )
        worksheet.write(row, 1, "", total_format)
        worksheet.write(row, 2, "", total_format)

        workbook.close()

        buffer.seek(0)
        await client.upload_file(upload_url, buffer.read())

        return await client.publish_file(path)
