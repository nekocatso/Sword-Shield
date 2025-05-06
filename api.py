import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from sword.sword import sword as _sword
from bs4 import BeautifulSoup

# from spider.spider import spider # Not used in API endpoints
from shield.shield import Shield

# from toTable import write2table # Not used in API endpoints

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize Shield model
shield_model = Shield()

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# Define sword endpoint
@app.route("/sword", methods=["POST"])
def handle_sword():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400
    try:
        # Extract text from body if HTML is provided
        soup = BeautifulSoup(text, "html.parser")
        body = soup.find("body")
        if body:
            body_text = body.get_text()
        else:
            # If no body tag, analyze the whole text
            body_text = (
                soup.get_text() if soup.get_text() else text
            )  # Get text from soup or use original if soup is empty

        keywords = _sword(body_text)
        return jsonify({"keywords": keywords})
    except AttributeError as ae:
        logging.error(
            f"Error extracting text from HTML in /sword: {ae}. Analyzing raw text as fallback."
        )
        # Fallback to analyzing the original text if specific parsing fails
        try:
            keywords = _sword(text)
            return jsonify(
                {
                    "keywords": keywords,
                    "warning": "Could not parse HTML effectively, analyzed raw text.",
                }
            )
        except Exception as e_fallback:
            logging.error(f"Error in /sword fallback analysis: {e_fallback}")
            return jsonify({"error": f"Failed to analyze text: {e_fallback}"}), 500
    except Exception as e:
        logging.error(f"Unexpected error in /sword: {e}")
        # General fallback or specific error handling
        try:
            keywords = _sword(
                text
            )  # Try with original text if parsing fails unexpectedly
            return jsonify(
                {
                    "keywords": keywords,
                    "warning": "An unexpected error occurred during HTML parsing, analyzed raw text.",
                }
            )
        except Exception as e_final_fallback:
            logging.error(
                f"Error in /sword final fallback analysis: {e_final_fallback}"
            )
            return (
                jsonify({"error": f"Failed to analyze text: {e_final_fallback}"}),
                500,
            )


# Define shield endpoint
@app.route("/shield", methods=["POST"])
def handle_shield():
    data = request.get_json()
    html_content = data.get("html", "")
    if not html_content:
        return jsonify({"error": "No HTML content provided"}), 400
    try:
        # Shield expects HTML content
        # Use the __call__ method directly as per commander.py usage
        result_label = shield_model(html_content)
        return jsonify({"result": result_label})
    except Exception as e:
        logging.error(f"Error in /shield: {e}")  # Use logging
        return jsonify({"error": str(e)}), 500


# Run the Flask server
if __name__ == "__main__":
    # Make sure to run on 0.0.0.0 to be accessible from other containers/machines if needed
    # Default Flask port is 5000, which matches the frontend config
    app.run(host="0.0.0.0", port=5000, debug=True)  # Added debug=True for development
