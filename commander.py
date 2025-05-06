from spider.spider import spider
from sword.sword import sword
from shield.shield import Shield
from toTable import write2table
from time import time
import sys
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

FILE_PATH = "url_list.txt"

if len(sys.argv) == 2:
    FILE_PATH = sys.argv[1]

with open(FILE_PATH, encoding="utf-8") as f:
    url_list = [line.strip() for line in f]

if __name__ == "__main__":
    shield_model = Shield()

    response = spider(url_list)
    result = {}
    t = time()
    logging.info("检查中...")
    if isinstance(response, dict):
        for url in response:
            if isinstance(response[url], str) and response[url].startswith(
                "错误:"
            ):  # Changed "ERROR:" to "错误:"
                logging.warning(
                    f"由于爬虫错误跳过 {url}: {response[url]}"
                )  # 使用日志记录
                result[url] = {"sword": "爬虫错误", "shield": "爬虫错误"}
                continue

            html_content = response.get(url)
            if not html_content:
                logging.warning(f"由于爬虫返回内容为空跳过 {url}。")  # 使用日志记录
                result[url] = {
                    "sword": "爬虫模块错误 - 内容为空",
                    "shield": "爬虫模块错误 - 内容为空",
                }
                continue

            result[url] = {}
            result[url]["sword"] = sword(html_content)
            shield_prediction_label = shield_model(
                html_content
            )  # 使用 __call__ 代替 predict
            result[url]["shield"] = shield_prediction_label  # 直接分配返回的标签

    else:
        logging.error("错误：爬虫未返回预期的字典格式。")  # 使用日志记录
        result = {"error": "爬虫失败"}

    logging.info(f"完成，耗时 {time() - t}秒")  # 使用日志记录
    logging.info("写入EXCEL...")  # 使用日志记录

    if "error" not in result:
        # 将处理后的结果字典传递给 write2table
        write2table(result)
    else:
        logging.error("跳过Excel处理，爬虫模块错误。")  # 使用日志记录

    logging.info("完成")  # 使用日志记录
