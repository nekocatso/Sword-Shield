import asyncio
from pyppeteer import launch
from config.config import *
import time
import logging  # Import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Define the async function to get a page
async def get_page(browser, url, result_dict):  # Accept browser instance
    page = None  # Initialize page to None
    try:
        page = await browser.newPage()
        logging.info("Start:" + url)  # Use logging
        # Increase timeout if needed, default is 30s
        await page.goto(
            url, {"waitUntil": "domcontentloaded", "timeout": 60000}
        )  # Wait until dom loaded, 60s timeout
        await asyncio.sleep(
            LOAD_TIME
        )  # Keep existing sleep if specific interaction timing is needed
        content = await page.content()
        result_dict[url] = content
        logging.info("Finish:" + url)  # Use logging
    except Exception as e:
        logging.error(f"Error processing {url}: {e}")  # Log specific error
        result_dict[url] = f"ERROR:{e}"
    finally:
        if page:
            try:
                await page.close()  # Close the page, not the browser
            except Exception as close_e:
                # Log error during page close if it happens
                logging.error(f"Error closing page for {url}: {close_e}")  # Use logging
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
            # Remove executablePath and userDataDir to use bundled Chromium
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
            logging.error(
                f"An error occurred in the task group: {group_e}"
            )  # Use logging
        # If not Python 3.11+, use gather:
        # tasks = [get_page(browser, url, result) for url in url_list]
        # await asyncio.gather(*tasks, return_exceptions=True) # return_exceptions to prevent one failure stopping all

    finally:
        if browser:
            try:
                await browser.close()  # Close the browser once after all tasks are done
            except Exception as close_e:
                logging.error(f"Error closing browser: {close_e}")  # Use logging

    return result


# Synchronous wrapper function
def spider(url_list: list) -> dict:
    t = time.time()
    logging.info("Spider Start")  # Use logging
    # Use asyncio.run() to manage the event loop
    results = asyncio.run(main(url_list))
    logging.info(f"Spider Finish, Spend {time.time() - t}s")  # Use logging
    return results
