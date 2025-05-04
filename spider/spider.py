import asyncio
from pyppeteer import launch
from config.config import *
import time


# Define the async function to get a page
async def get_page(browser, url, result_dict):  # Accept browser instance
    page = None  # Initialize page to None
    try:
        page = await browser.newPage()
        print("Start:" + url)
        # Increase timeout if needed, default is 30s
        await page.goto(
            url, {"waitUntil": "domcontentloaded", "timeout": 60000}
        )  # Wait until dom loaded, 60s timeout
        await asyncio.sleep(
            LOAD_TIME
        )  # Keep existing sleep if specific interaction timing is needed
        content = await page.content()
        result_dict[url] = content
        print("Finish:" + url)
    except Exception as e:
        print(f"Error processing {url}: {e}")  # Log specific error
        result_dict[url] = f"ERROR:{e}"
    finally:
        if page:
            try:
                await page.close()  # Close the page, not the browser
            except Exception as close_e:
                # Log error during page close if it happens
                print(f"Error closing page for {url}: {close_e}")
        # Do not close the browser here


# Define the main async function to run all tasks
async def main(url_list):
    result = {}
    browser = None  # Initialize browser to None outside the loop
    try:
        browser = await launch(
            ignoreHTTPSErrors=True,
            args=[
                "--disable-infobars",
                f"--window-size={WIDTH},{HEIGHT}",
                "--blink-settings=imagesEnabled=false",
                "--no-sandbox",
            ],
            executablePath="D:\Chrome\App\chrome.exe",  # Use existing Chrome (escaped backslashes)
            # executablePath = './bin/chrome-linux/chrome'
            # executablePath = './bin/chrome-win32/chrome.exe',
            userDataDir="./tmp",
            handleSIGINT=False,
            handleSIGTERM=False,
            handleSIGHUP=False,
            # autoClose=False # Keep browser open until explicitly closed
        )

        # Use asyncio.TaskGroup for better task management (requires Python 3.11+)
        # If using older Python, stick to asyncio.gather
        # Assuming Python 3.11+ for TaskGroup example
        try:
            async with asyncio.TaskGroup() as tg:
                for url in url_list:
                    # Pass the single browser instance to each task
                    tg.create_task(get_page(browser, url, result))
        except Exception as group_e:
            print(f"An error occurred in the task group: {group_e}")
        # If not Python 3.11+, use gather:
        # tasks = [get_page(browser, url, result) for url in url_list]
        # await asyncio.gather(*tasks, return_exceptions=True) # return_exceptions to prevent one failure stopping all

    finally:
        if browser:
            try:
                await browser.close()  # Close the browser once after all tasks are done
            except Exception as close_e:
                print(f"Error closing browser: {close_e}")

    return result


# Synchronous wrapper function
def spider(url_list: list) -> dict:
    t = time.time()
    print("Spider Start")
    # Use asyncio.run() to manage the event loop
    results = asyncio.run(main(url_list))
    print(f"Spider Finish, Spend {time.time() - t}s")
    return results
