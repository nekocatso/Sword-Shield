import gradio as gr
import requests
import pandas as pd  # Import pandas for DataFrame conversion

API_BASE_URL = "http://127.0.0.1:5000/api"  # Updated to include /api prefix


def handle_api_response(response_json, success_key=None):
    """Helper function to handle API JSON responses and errors."""
    if isinstance(response_json, str):  # Raw error string from requests exception
        return {"error": response_json}
    if "error" in response_json:
        return response_json
    if (
        success_key
        and success_key not in response_json
        and not isinstance(response_json, list)
    ):
        return {"error": f"API did not return expected data: {success_key} missing"}
    return response_json


def analyze_single_url(url):
    if not url:
        return "URL不能为空。", None, None
    try:
        response = requests.post(f"{API_BASE_URL}/analyze_url", json={"url": url})
        response.raise_for_status()
        data = handle_api_response(response.json())
        if "error" in data:
            return data["error"], None, None

        # Format for Gradio output
        shield_result_text = data.get("shield_result", "N/A")
        # Convert sword_result list to a DataFrame for table display
        sword_df = pd.DataFrame(data.get("sword_result", []), columns=["敏感词"])
        html_tags_json = data.get("html_tags", {})
        return shield_result_text, sword_df, html_tags_json
    except requests.exceptions.ConnectionError as e:
        return (
            f"无法连接到后端API ({API_BASE_URL}): {e}. 请确保后端服务 (app.py) 正在运行，并且端口5000可用，同时没有其他程序(如api.py)占用了此端口。",
            None,
            None,
        )
    except requests.exceptions.RequestException as e:
        return f"调用API时出错: {e}", None, None
    except Exception as e:
        return f"处理响应时出错: {e}", None, None


def analyze_batch_urls(urls_text):
    if not urls_text:
        return None, "URL列表不能为空。"
    urls = [u.strip() for u in urls_text.split("\n") if u.strip()]
    if not urls:
        return None, "未提供有效URL。"
    try:
        response = requests.post(f"{API_BASE_URL}/analyze_urls", json={"urls": urls})
        response.raise_for_status()
        data = handle_api_response(response.json())
        if "error" in data:
            return None, data["error"]

        # The API returns { "results": [...], "summary": {...} }
        # We need to convert the "results" list of dicts into a DataFrame
        results_list = data.get("results", [])
        if not results_list:
            return None, "未返回分析结果。"

        # Convert list of dicts to DataFrame
        df = pd.DataFrame(results_list)
        # Ensure columns are in a consistent order, handling missing keys gracefully
        cols = ["url", "shield_result", "sword_result", "status"]
        df = df.reindex(columns=cols).fillna("N/A")
        # Convert list of keywords to string for display in DataFrame
        df["sword_result"] = df["sword_result"].apply(
            lambda x: ", ".join(x) if isinstance(x, list) else str(x)
        )

        summary = data.get("summary", {})
        summary_text = f"总结: 总计: {summary.get('total',0)}, 恶意: {summary.get('malicious',0)}, 正常: {summary.get('normal',0)}, 错误: {summary.get('error',0)}"
        return df, summary_text
    except requests.exceptions.ConnectionError as e:
        return (
            None,
            f"无法连接到后端API ({API_BASE_URL}): {e}. 请确保后端服务 (app.py) 正在运行，并且端口5000可用，同时没有其他程序(如api.py)占用了此端口。",
        )
    except requests.exceptions.RequestException as e:
        return None, f"调用API时出错: {e}"
    except Exception as e:
        return None, f"处理响应时出错: {e}"


def analyze_html_file_or_content(html_file, html_content_text):
    content_to_analyze = ""
    if html_file is not None:
        try:
            # Gradio File object has a .name attribute which is the temp file path
            with open(html_file.name, "r", encoding="utf-8") as f:
                content_to_analyze = f.read()
        except Exception as e:
            return f"读取文件时出错: {e}", None, None
    elif html_content_text:
        content_to_analyze = html_content_text
    else:
        return "请提供HTML内容或上传HTML文件。", None, None

    if not content_to_analyze:
        return "HTML内容为空。", None, None

    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze_html", json={"html_content": content_to_analyze}
        )
        response.raise_for_status()
        data = handle_api_response(response.json())
        if "error" in data:
            return data["error"], None, None

        shield_result_text = data.get("shield_result", "N/A")
        sword_df = pd.DataFrame(data.get("sword_result", []), columns=["敏感词"])
        html_tags_json = data.get("html_tags", {})
        return shield_result_text, sword_df, html_tags_json
    except requests.exceptions.ConnectionError as e:
        return (
            f"无法连接到后端API ({API_BASE_URL}): {e}. 请确保后端服务 (app.py) 正在运行，并且端口5000可用，同时没有其他程序(如api.py)占用了此端口。",
            None,
            None,
        )
    except requests.exceptions.RequestException as e:
        return f"调用API时出错: {e}", None, None
    except Exception as e:
        return f"处理响应时出错: {e}", None, None


exported_file_path_cache = None  # Cache for the last exported file path


def export_results_to_excel(batch_results_df):
    global exported_file_path_cache
    if batch_results_df is None or batch_results_df.empty:
        exported_file_path_cache = None
        return "没有可导出的结果。", None  # Return None for the file download component

    # Convert DataFrame back to the list of dicts format expected by the backend export API
    # The backend /api/export_excel expects a list under the key "results"
    # Each item in the list should be a dict like: {"url": ..., "shield_result": ..., "sword_result": ...}

    # Check if 'sword_result' column exists and if it needs conversion from string to list
    if "sword_result" in batch_results_df.columns:
        # Assuming sword_result is a comma-separated string, convert it back to a list of strings
        # If it might already be a list (e.g., if API changes), handle that too.
        data_to_export = batch_results_df.apply(
            lambda row: {
                "url": row.get("url"),
                "shield_result": row.get("shield_result"),
                "sword_result": (
                    [
                        s.strip()
                        for s in row.get("sword_result", "").split(",")
                        if s.strip()
                    ]
                    if isinstance(row.get("sword_result"), str)
                    else row.get("sword_result", [])
                ),
            },
            axis=1,
        ).tolist()
    else:  # Fallback if 'sword_result' column is missing for some reason
        data_to_export = batch_results_df.apply(
            lambda row: {
                "url": row.get("url"),
                "shield_result": row.get("shield_result"),
                "sword_result": [],  # Default to empty list
            },
            axis=1,
        ).tolist()

    try:
        response = requests.post(
            f"{API_BASE_URL}/export_excel", json={"results": data_to_export}
        )
        response.raise_for_status()
        data = handle_api_response(response.json(), success_key="download_url")
        if "error" in data:
            exported_file_path_cache = None
            return data["error"], None

        # The backend now returns a relative path like /exports/filename.xls
        # We need to construct the full URL for the download
        # Assuming API_BASE_URL is http://127.0.0.1:5000/api, we need to strip /api for file download
        base_download_url = API_BASE_URL.replace("/api", "")
        full_download_url = f"{base_download_url}{data['download_url']}"
        exported_file_path_cache = full_download_url  # Cache the full URL

        # Gradio File component expects a local filepath or a URL for download.
        # For simplicity, we can provide a direct download link as a Markdown component
        # or rely on the user to copy the URL. The gr.File component can also take a URL.
        return f"Excel文件已生成: [下载链接]({full_download_url})", full_download_url

    except requests.exceptions.ConnectionError as e:
        exported_file_path_cache = None
        return (
            f"无法连接到后端API ({API_BASE_URL}): {e}. 请确保后端服务 (app.py) 正在运行，并且端口5000可用，同时没有其他程序(如api.py)占用了此端口。",
            None,
        )
    except requests.exceptions.RequestException as e:
        exported_file_path_cache = None
        return f"调用API时出错: {e}", None
    except Exception as e:
        exported_file_path_cache = None
        return f"处理响应时出错: {e}", None


with gr.Blocks(title="Sword-Shield 网页安全分析系统") as demo:
    gr.Markdown("# Sword-Shield 网页安全分析系统")

    with gr.Tabs():
        with gr.TabItem("单一URL分析"):
            url_input = gr.Textbox(label="输入网址")
            analyze_btn = gr.Button("分析")

            with gr.Accordion("分析结果", open=False):
                security_label = gr.Label(label="安全评估")
                keywords_table = gr.DataFrame(
                    label="检测到的敏感词", headers=["敏感词"]
                )
                html_analysis = gr.JSON(label="HTML标签分析")

            analyze_btn.click(
                fn=analyze_single_url,
                inputs=url_input,
                outputs=[security_label, keywords_table, html_analysis],
            )

        with gr.TabItem("批量URL分析"):
            urls_input = gr.Textbox(label="输入多个URL（每行一个）", lines=10)
            batch_analyze_btn = gr.Button("批量分析")

            batch_results_df = gr.DataFrame(label="批量分析结果")
            batch_summary_text = gr.Textbox(label="分析总结", interactive=False)

            export_button = gr.Button("导出Excel")
            export_status_text = gr.Markdown(
                label="导出状态"
            )  # For messages like "Excel generated..."
            # Hidden component to trigger download, or use Markdown link
            # file_download = gr.File(label="下载导出的Excel")
            # Using Markdown for a direct link is often simpler if the backend provides a URL.

            batch_analyze_btn.click(
                fn=analyze_batch_urls,
                inputs=urls_input,
                outputs=[batch_results_df, batch_summary_text],
            )
            export_button.click(
                fn=export_results_to_excel,
                inputs=batch_results_df,  # Pass the DataFrame containing results
                outputs=[
                    export_status_text,
                    gr.File(label="下载链接", value=None, visible=True),
                ],  # Use a File component for download
            )

        with gr.TabItem("HTML内容分析"):
            # Combined input: either text or file
            html_text_input = gr.Textbox(label="粘贴HTML内容", lines=10)
            html_file_input = gr.File(label="或上传HTML文件")
            html_analyze_btn = gr.Button("分析HTML")

            with gr.Accordion("分析结果", open=False):
                html_security_label = gr.Label(label="安全评估")
                html_keywords_table = gr.DataFrame(
                    label="检测到的敏感词", headers=["敏感词"]
                )
                html_tags_analysis = gr.JSON(label="HTML标签分析")

            html_analyze_btn.click(
                fn=analyze_html_file_or_content,
                inputs=[
                    html_file_input,
                    html_text_input,
                ],  # Order matters for the function
                outputs=[html_security_label, html_keywords_table, html_tags_analysis],
            )
demo.launch()
