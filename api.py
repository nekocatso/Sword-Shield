from flask import Flask, request, jsonify
from flask_cors import CORS
from sword.sword import sword as _sword
from bs4 import BeautifulSoup

# from spider.spider import spider # Not used in API endpoints
from shield.shield import Shield

# from toTable import write2table # Not used in API endpoints

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
        body_text = soup.find("body").get_text() if soup.find("body") else text
        keywords = _sword(body_text)
        return jsonify({"keywords": keywords})
    except Exception as e:
        print(f"Error in /sword: {e}")
        # Fallback or specific error handling
        keywords = _sword(text)  # Try with original text if parsing fails
        return jsonify(
            {
                "keywords": keywords,
                "warning": "Could not parse HTML body, analyzed raw text.",
            }
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
        result = shield_model.predict(
            html_content
        )  # Assuming shield_model has a predict method
        # Map result to the format expected by the frontend
        is_evil_str = (
            "恶意网页" if result == 0 else "正常网页"
        )  # Assuming 0 is malicious, 1 is normal based on train.ipynb
        return jsonify({"result": is_evil_str})
    except Exception as e:
        print(f"Error in /shield: {e}")
        return jsonify({"error": str(e)}), 500


# Run the Flask server
if __name__ == "__main__":
    # Make sure to run on 0.0.0.0 to be accessible from other containers/machines if needed
    # Default Flask port is 5000, which matches the frontend config
    app.run(host="0.0.0.0", port=5000, debug=True)  # Added debug=True for development
