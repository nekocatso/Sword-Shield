import xlwt
import time
import os

EXPORT_DIR = "exports"  # Define the export directory name


def write2table(
    result_data,
):  # Renamed 'result' to 'result_data' to avoid potential conflicts
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)  # Create the directory if it doesn't exist

    book = xlwt.Workbook(encoding="utf-8")
    sheet = book.add_sheet("测试结果")
    sheet.write(0, 0, "目标URL")
    sheet.write(0, 1, "是否包含恶意代码")
    sheet.write(0, 2, "敏感词检测结果")

    row_idx = 1
    for url, data in result_data.items():  # Iterate through items for clarity
        sheet.write(row_idx, 0, url)
        sheet.write(row_idx, 1, data.get("shield", "N/A"))  # Use .get for safety
        sword_results = data.get("sword", [])
        if isinstance(sword_results, list):
            sheet.write(row_idx, 2, ",".join(sword_results))
        else:
            sheet.write(row_idx, 2, str(sword_results))  # Handle if not a list
        row_idx += 1

    filename = str(time.time()).split(".")[0] + ".xls"
    filepath = os.path.join(EXPORT_DIR, filename)
    book.save(filepath)
    return filename  # Return only the filename
