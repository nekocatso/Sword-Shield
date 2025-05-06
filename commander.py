# Import directly from the source modules
from spider.spider import spider
from sword.sword import sword
from shield.shield import Shield  # Import the Shield class
from toTable import write2table
from time import time
import sys
import logging  # Import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

FILE_PATH = "url_list.txt"

if len(sys.argv) == 2:
    FILE_PATH = sys.argv[1]

with open(FILE_PATH, encoding="utf-8") as f:
    url_list = [line.strip() for line in f]

if __name__ == "__main__":
    # Instantiate the Shield model
    shield_model = Shield()

    response = spider(url_list)
    result = {}
    t = time()
    logging.info("Checking...")  # Use logging
    if isinstance(response, dict):
        for url in response:
            if isinstance(response[url], str) and response[url].startswith("ERROR:"):
                logging.warning(
                    f"Skipping {url} due to spider error: {response[url]}"
                )  # Use logging
                result[url] = {"sword": "Spider Error", "shield": "Spider Error"}
                continue

            # Ensure response[url] is not None or empty before processing
            html_content = response.get(url)
            if not html_content:
                logging.warning(
                    f"Skipping {url} due to empty content from spider."
                )  # Use logging
                result[url] = {
                    "sword": "Spider Error - Empty Content",
                    "shield": "Spider Error - Empty Content",
                }
                continue

            result[url] = {}
            # Assuming sword function takes the HTML content directly
            result[url]["sword"] = sword(html_content)
            # Call the __call__ method on the shield_model instance by calling the object directly
            # Map result: 0 -> Malicious, 1 -> Normal
            shield_prediction_label = shield_model(
                html_content
            )  # Use __call__ instead of predict
            result[url][
                "shield"
            ] = shield_prediction_label  # Assign the returned label directly

    else:
        logging.error(
            "Error: Spider did not return the expected dictionary format."
        )  # Use logging
        result = {"error": "Spider failed"}

    logging.info(f"Finish, Spend {time() - t}s")  # Use logging
    logging.info("Write to EXCEL...")  # Use logging

    if "error" not in result:
        # Pass the processed result dictionary to write2table
        write2table(result)
    else:
        logging.error("Skipping writing to Excel due to spider error.")  # Use logging

    logging.info("Finish")  # Use logging
