import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from sword.sword import sword as _sword
from bs4 import BeautifulSoup
from shield.shield import Shield

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

shield_model = Shield()

# 创建Flask应用实例
app = Flask(__name__)
CORS(app)  # 为所有路由启用CORS


# 定义sword端点
@app.route("/sword", methods=["POST"])
def handle_sword():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "没有提供文本"}), 400
    try:
        # 如果提供的是HTML，则从body中提取文本
        soup = BeautifulSoup(text, "html.parser")
        body = soup.find("body")
        if body:
            body_text = body.get_text()
        else:
            body_text = soup.get_text() if soup.get_text() else text

        keywords = _sword(body_text)
        return jsonify({"keywords": keywords})
    except AttributeError as ae:
        logging.error(
            f"在获取HTML页面时sword部件出错: {ae}. 请检查HTML内容是否有效或包含body标签。"
        )
        # 如果特定的解析失败，则回退到分析原始文本
        try:
            keywords = _sword(text)
            return jsonify(
                {
                    "keywords": keywords,
                    "warning": "无法有效解析HTML，分析了原始文本。",
                }
            )
        except Exception as e_fallback:
            logging.error(f"在 /sword 回退分析中出错: {e_fallback}")
            return jsonify({"error": f"分析文本失败: {e_fallback}"}), 500
    except Exception as e:
        logging.error(f"在 /sword 时发生意外错误: {e}")
        # 通用回退或特定的错误处理
        try:
            keywords = _sword(text)  # 如果解析意外失败，则尝试使用原始文本
            return jsonify(
                {
                    "keywords": keywords,
                    "warning": "HTML解析过程中发生意外错误，已分析原始文本。",
                }
            )
        except Exception as e_final_fallback:
            logging.error(f"在 /sword 最终回退分析中出错: {e_final_fallback}")
            return (
                jsonify({"error": f"分析文本失败: {e_final_fallback}"}),
                500,
            )


# 定义shield端点
@app.route("/shield", methods=["POST"])
def handle_shield():
    data = request.get_json()
    html_content = data.get("html", "")
    if not html_content:
        return jsonify({"error": "没有提供HTML内容"}), 400
    try:
        result_label = shield_model(html_content)
        return jsonify({"result": result_label})
    except Exception as e:
        logging.error(f"在 /shield 时出错: {e}")  # 使用日志记录错误
        return jsonify({"error": str(e)}), 500


# 运行Flask开发服务器
if __name__ == "__main__":
    app.run(host="192.168.0.1", port=5000, debug=True)
