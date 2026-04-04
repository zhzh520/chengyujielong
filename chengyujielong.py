from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# 全局历史
history = []
idioms = set()

# 加载你的成语库 txt
try:
    with open(r"D:\Users\huihu\Desktop\2026\damoxing\RAG\链代码\chengyuku.txt", "r", encoding="utf-8") as f:
        for line in f:
            c = line.strip()
            if len(c) == 4:
                idioms.add(c)
    print(f"✅ 成语库加载成功：共 {len(idioms)} 个四字成语")
except:
    print("⚠️ 未找到 chengyuku.txt，将使用 AI 自由接龙")

OLLAMA_API = "http://localhost:11434/api/generate"

# 前端页面（内置）
HTML = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧩 成语接龙 </title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
        }

        body {
            background: linear-gradient(135deg, #f0f4ff, #d9e2ff);
            min-height: 100vh;
            padding: 30px 20px;
        }

        .container {
            max-width: 720px;
            margin: 0 auto;
        }

        .card {
            background: #ffffff;
            border-radius: 20px;
            box-shadow: 0 8px 30px rgba(0, 30, 80, 0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(90deg, #4a6cf7, #3498db);
            color: white;
            padding: 22px 24px;
            font-size: 24px;
            font-weight: bold;
            text-align: center;
        }

        .chat-box {
            height: 540px;
            padding: 24px;
            overflow-y: auto;
            background: #fafbfc;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .bubble {
            max-width: 75%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 16px;
            line-height: 1.5;
            position: relative;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .user-bubble {
            background: #4a6cf7;
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 6px;
        }

        .ai-bubble {
            background: white;
            color: #2c3e50;
            border: 1px solid #e4e7ed;
            align-self: flex-start;
            border-bottom-left-radius: 6px;
        }

        .input-bar {
            display: flex;
            gap: 12px;
            padding: 20px 24px;
            background: white;
            border-top: 1px solid #f0f2f5;
        }

        .input-bar input {
            flex: 1;
            padding: 16px 20px;
            border: 1px solid #e4e7ed;
            border-radius: 16px;
            font-size: 16px;
            outline: none;
            transition: all 0.2s;
        }

        .input-bar input:focus {
            border-color: #4a6cf7;
            box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.15);
        }

        .btn {
            padding: 16px 24px;
            border-radius: 16px;
            font-size: 16px;
            font-weight: 500;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-send {
            background: #4a6cf7;
            color: white;
        }

        .btn-send:hover {
            background: #3a5ce2;
        }

        .btn-clear {
            background: #f5f7fa;
            color: #7b8496;
        }

        .btn-clear:hover {
            background: #e4e7ed;
        }

        .tip {
            text-align: center;
            margin-top: 16px;
            color: #64748b;
            font-size: 14px;
        }

        /* 滚动条美化 */
        .chat-box::-webkit-scrollbar {
            width: 6px;
        }
        .chat-box::-webkit-scrollbar-thumb {
            background: #d1d5db;
            border-radius: 10px;
        }
    </style>
</head>

<body>
    <div class="container">
        <div class="card">
            <div class="header">🧩 成语接龙 </div>
            <div class="chat-box" id="chat"></div>
            <div class="input-bar">
                <input id="i" placeholder="请输入四字成语，按回车发送">
                <button class="btn btn-send" onclick="send()">发送</button>
                <button class="btn btn-clear" onclick="clearChat()">清空</button>
            </div>
        </div>
        <div class="tip">✅ 优先使用本地成语库 | 📚 智能 AI 兜底</div>
    </div>

    <script>
        async function send(){
            const v = document.getElementById("i").value.trim();
            if(!v) return alert("请输入成语！");
            document.getElementById("i").value = "";

            const res = await fetch("/play", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ idiom: v })
            });

            const d = await res.json();
            render(d.history);
        }

        function render(h){
            const dom = document.getElementById("chat");
            dom.innerHTML = "";

            h.forEach(item => {
                const div = document.createElement("div");
                if (item.user) {
                    div.className = "bubble user-bubble";
                    div.innerText = item.user;
                } else {
                    div.className = "bubble ai-bubble";
                    div.innerText = item.ai;
                }
                dom.appendChild(div);
            });

            dom.scrollTop = dom.scrollHeight;
        }

        async function clearChat(){
            await fetch("/clear", { method: "POST" });
            render([]);
        }

        window.onload = async () => {
            const d = await (await fetch("/history")).json();
            render(d.history);
        };

        document.getElementById("i").addEventListener("keydown", e => {
            if (e.key === "Enter") send();
        });
    </script>
</body>
</html>
'''


# 从成语库找接龙
def find_idiom_from_lib(last_char):
    for c in idioms:
        if c.startswith(last_char):
            return c
    return None


# AI 兜底
def ai_get(idiom):
    last = idiom[-1]
    prompt = f"""成语接龙，用【{last}】开头，只返回一个四字成语，不要其他内容。"""
    try:
        r = requests.post(OLLAMA_API, json={
            "model": "gemma3:4b", "prompt": prompt, "stream": False
        })
        res = r.json()["response"].strip()
        return res if len(res) == 4 else None
    except:
        return None


# 路由
@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/play", methods=["POST"])
def play():
    user = request.json.get("idiom", "").strip()
    if not user or len(user) != 4:
        return jsonify({"ok": 0, "msg": "请输入四字成语"})

    history.append({"user": user})
    last = user[-1]

    # 优先从你的成语库取
    ai = find_idiom_from_lib(last)

    # 成语库没有 → AI 兜底
    if not ai:
        ai = ai_get(user) or "⚠️ 接不上啦！"

    history.append({"ai": ai})
    return jsonify({"history": history})


@app.route("/history")
def hist():
    return jsonify({"history": history})


@app.route("/clear", methods=["POST"])
def clear():
    global history
    history = []
    return jsonify({"ok": 1})


if __name__ == "__main__":
    print("🚀 启动成功！访问：http://127.0.0.1:5000")
    app.run(port=5000, debug=True)