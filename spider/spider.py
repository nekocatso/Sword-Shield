import asyncio
from pyppeteer import launch
from config.config import *
import time
import logging  # 导入日志模块

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# 定义异步函数来获取页面
async def get_page(browser, url, result_dict):  # 接受浏览器实例
    page = None  # 初始化页面为None
    try:
        page = await browser.newPage()
        logging.info("开始:" + url)  # 使用日志
        # 如果需要，增加超时时间，默认为30秒
        await page.goto(
            url, {"waitUntil": "domcontentloaded", "timeout": 60000}
        )  # 等待DOM加载完成，60秒超时
        await asyncio.sleep(LOAD_TIME)  # 如果需要特定的交互时间，则保留现有的睡眠时间
        content = await page.content()
        result_dict[url] = content
        logging.info("完成:" + url)  # 使用日志
    except Exception as e:
        logging.error(f"处理 {url} 时出错: {e}")  # 记录特定错误
        result_dict[url] = f"错误:{e}"
    finally:
        if page:
            try:
                await page.close()  # 关闭页面，而不是浏览器
            except Exception as close_e:
                # 如果发生错误，记录页面关闭期间的错误
                logging.error(f"关闭 {url} 页面时出错: {close_e}")  # 使用日志
        # 此处不要关闭浏览器


# 定义主异步函数以运行所有任务
async def main(url_list):
    result = {}
    browser = None  # 在循环外部将浏览器初始化为None
    try:
        browser = await launch(
            executablePath="./bin/Chrome/App/chrome.exe",  # Specify Chrome path
            ignoreHTTPSErrors=True,
            args=[
                "--disable-infobars",
                f"--window-size={WIDTH},{HEIGHT}",
                "--blink-settings=imagesEnabled=false",
                "--no-sandbox",
            ],
            # 移除executablePath和userDataDir以使用捆绑的Chromium
            handleSIGINT=False,
            handleSIGTERM=False,
            handleSIGHUP=False,
            autoClose=False,  # 保持浏览器打开直到显式关闭
        )

        # 使用asyncio.TaskGroup进行更好的任务管理（需要Python 3.11+）
        # 如果使用较旧的Python，请坚持使用asyncio.gather
        # 假设使用Python 3.11+的TaskGroup示例
        try:
            async with asyncio.TaskGroup() as tg:
                for url in url_list:
                    # 将单个浏览器实例传递给每个任务
                    tg.create_task(get_page(browser, url, result))
        except Exception as group_e:
            logging.error(f"任务组中发生错误: {group_e}")  # 使用日志
        # 如果不是Python 3.11+，请使用gather：
        # tasks = [get_page(browser, url, result) for url in url_list]
        # await asyncio.gather(*tasks, return_exceptions=True) # return_exceptions以防止一个故障停止所有故障

    finally:
        if browser:
            try:
                await browser.close()  # 所有任务完成后关闭浏览器
            except Exception as close_e:
                logging.error(f"关闭浏览器时出错: {close_e}")  # 使用日志

    return result


# 同步包装函数
def spider(url_list: list) -> dict:
    t = time.time()
    logging.info("爬虫开始")  # 使用日志
    # 使用asyncio.run()管理事件循环
    results = asyncio.run(main(url_list))
    logging.info(f"爬虫完成，耗时 {time.time() - t}秒")  # 使用日志
    return results
