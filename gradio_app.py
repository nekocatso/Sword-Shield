import gradio as gr
import requests
import json

# Define the base URL for the Flask API
API_BASE_URL = "http://127.0.0.1:5000"  # Assuming the Flask app runs on port 5000


def detect_html_content_gradio(html_content):
    if not html_content:
        return "Please provide HTML content."
    try:
        response = requests.post(
            f"{API_BASE_URL}/detect_html_content", json={"html_content": html_content}
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"
    except json.JSONDecodeError:
        return "Error: Could not decode JSON response from API."


def detect_url_gradio(urls_string):
    if not urls_string:
        return "Please provide at least one URL."
    url_list = [url.strip() for url in urls_string.split(",")]
    if not url_list:
        return "No valid URLs provided after stripping whitespace."
    try:
        response = requests.post(f"{API_BASE_URL}/detect_urls", json={"urls": url_list})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"
    except json.JSONDecodeError:
        return "Error: Could not decode JSON response from API."


def get_model_status_gradio():
    try:
        response = requests.get(f"{API_BASE_URL}/model_status")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"
    except json.JSONDecodeError:
        return "Error: Could not decode JSON response from API."


with gr.Blocks() as demo:
    gr.Markdown("# Sword-Shield Web Analysis Tool")

    with gr.Tab("HTML Content Analysis"):
        with gr.Row():
            html_input = gr.Textbox(
                lines=10, label="HTML Content", placeholder="Paste HTML content here..."
            )
        with gr.Row():
            analyze_html_button = gr.Button("Analyze HTML")
        with gr.Row():
            html_output = gr.JSON(label="Analysis Result")
        analyze_html_button.click(
            detect_html_content_gradio, inputs=html_input, outputs=html_output
        )

    with gr.Tab("URL Analysis"):
        with gr.Row():
            url_input = gr.Textbox(
                label="URLs (comma-separated)",
                placeholder="e.g., http://example.com, http://test.org",
            )
        with gr.Row():
            analyze_url_button = gr.Button("Analyze URLs")
        with gr.Row():
            url_output = gr.JSON(label="Analysis Results")
        analyze_url_button.click(
            detect_url_gradio, inputs=url_input, outputs=url_output
        )

    with gr.Tab("Model Status"):
        with gr.Row():
            status_button = gr.Button("Refresh Status")
        with gr.Row():
            status_output = gr.JSON(label="Model Status")
        status_button.click(get_model_status_gradio, inputs=None, outputs=status_output)

if __name__ == "__main__":
    demo.launch()
