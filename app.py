import logging
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from bs4 import BeautifulSoup

# Project-specific imports
from spider.spider import spider
from sword.sword import sword as _sword
from shield.shield import Shield
from toTable import write2table, EXPORT_DIR  # Import EXPORT_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize Flask app and Shield model
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
shield_model = Shield()

# Ensure the export directory exists
if not os.path.exists(EXPORT_DIR):
    os.makedirs(EXPORT_DIR)


def extract_html_tags(html_content: str) -> list[str]:
    """Extracts unique HTML tag names from HTML content."""
    if not html_content:
        return []
    soup = BeautifulSoup(html_content, "html.parser")
    tags = set()
    for tag_element in soup.find_all(True):  # True matches all tags
        tags.add(tag_element.name)
    return sorted(list(tags))


@app.route("/api/analyze_url", methods=["POST"])
def analyze_url_route():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        spider_result = spider([url])
        html_content = spider_result.get(url)

        if not html_content or html_content.startswith("错误:"):
            return (
                jsonify(
                    {
                        "url": url,
                        "shield_result": "N/A",
                        "sword_result": [],
                        "html_tags": [],
                        "status": f"Failed to fetch or process URL: {html_content if html_content else 'No content'}",
                    }
                ),
                200,
            )  # Return 200 as the operation to analyze was attempted

        shield_result = shield_model(html_content)
        sword_result = _sword(html_content)
        html_tags = extract_html_tags(html_content)

        return jsonify(
            {
                "url": url,
                "shield_result": shield_result,
                "sword_result": sword_result,
                "html_tags": html_tags,
                "status": "Success",
            }
        )

    except Exception as e:
        logging.error(f"Error in /api/analyze_url for {url}: {e}")
        return jsonify({"error": str(e), "status": "Failed"}), 500


@app.route("/api/analyze_urls", methods=["POST"])
def analyze_urls_route():
    data = request.get_json()
    urls = data.get("urls")

    if not urls or not isinstance(urls, list):
        return jsonify({"error": "A list of URLs is required"}), 400

    results = []
    summary = {"total": len(urls), "malicious": 0, "normal": 0, "error": 0}

    spider_results = spider(urls)  # Batch crawl

    for url in urls:
        html_content = spider_results.get(url)

        if not html_content or html_content.startswith("错误:"):
            results.append(
                {
                    "url": url,
                    "shield_result": "N/A",
                    "sword_result": [],
                    "status": f"Failed to fetch or process URL: {html_content if html_content else 'No content'}",
                }
            )
            summary["error"] += 1
            continue

        try:
            shield_result = shield_model(html_content)
            sword_result = _sword(html_content)
            # html_tags = extract_html_tags(html_content) # Not in spec for batch results items

            results.append(
                {
                    "url": url,
                    "shield_result": shield_result,
                    "sword_result": sword_result,
                    "status": "Success",
                }
            )

            if shield_result == shield_model.label_map[0]:  # Assuming 0 is malicious
                summary["malicious"] += 1
            else:
                summary["normal"] += 1

        except Exception as e:
            logging.error(f"Error processing {url} in batch: {e}")
            results.append(
                {
                    "url": url,
                    "shield_result": "Error",
                    "sword_result": [],
                    "status": f"Processing error: {str(e)}",
                }
            )
            summary["error"] += 1

    return jsonify({"results": results, "summary": summary})


@app.route("/api/analyze_html", methods=["POST"])
def analyze_html_route():
    data = request.get_json()
    html_content = data.get("html_content")

    if not html_content:
        return jsonify({"error": "HTML content is required"}), 400

    try:
        shield_result = shield_model(html_content)
        sword_result = _sword(html_content)
        html_tags = extract_html_tags(html_content)

        return jsonify(
            {
                "shield_result": shield_result,
                "sword_result": sword_result,
                "html_tags": html_tags,
            }
        )
    except Exception as e:
        logging.error(f"Error in /api/analyze_html: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/export_excel", methods=["POST"])
def export_excel_route():
    data = request.get_json()
    analysis_data = data.get("results")  # Expects the list of result objects

    if not analysis_data or not isinstance(analysis_data, list):
        return jsonify({"error": "Analysis data (list of results) is required"}), 400

    results_for_table = {}
    for item in analysis_data:
        # Ensure 'url', 'shield_result', and 'sword_result' keys exist
        url = item.get("url")
        if not url:  # Skip items without a URL, though ideally all should have one
            continue
        results_for_table[url] = {
            "shield": item.get("shield_result", "N/A"),
            "sword": item.get("sword_result", []),
        }

    if not results_for_table:
        return jsonify({"error": "No valid data to export"}), 400

    try:
        filename = write2table(results_for_table)
        # Return a URL that the frontend can use to trigger the download
        return jsonify({"download_url": f"/exports/{filename}"})
    except Exception as e:
        logging.error(f"Error in /api/export_excel: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/exports/<path:filename>", methods=["GET"])
def download_exported_file(filename):
    try:
        return send_from_directory(EXPORT_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        logging.error(f"Exported file not found: {filename}")
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        logging.error(f"Error serving exported file {filename}: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # It's good practice to not run debug mode in production.
    # The host='0.0.0.0' makes it accessible externally if needed.
    app.run(host="0.0.0.0", port=5000, debug=True)
