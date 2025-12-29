
from flask import Flask, request, jsonify, render_template, session
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "secret_key_for_session"
client = OpenAI(api_key="")

# 最大履歴数と質問回数制限
MAX_HISTORY = 20
MAX_QUERIES = 10

@app.route("/ui")
def ui():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    # セッション初期化（messagesとquery_count）
    if "messages" not in session:
        session["messages"] = [
            {"role": "system", "content": (
                "あなたは坂本龍馬です。現代にタイムスリップし、営業部長として働いています。"
                "歴史上の自分の出来事は覚えていますが、現代ビジネスにも精通しています。"
                "豪快で前向きな口調で、営業の悩みに答えてください。"
                "必要なら歴史的比喩も交えて、現代の営業戦略を提案してください。"
            )}
        ]
    
    if "query_count" not in session:
        session["query_count"] = 0

    # 回数制限チェック
    if session["query_count"] >= MAX_QUERIES:
        return jsonify({"reply": "回数制限に達しました。新しいセッションを開始してください（リセットボタンを押してください）。"})

    # ユーザー発言追加
    session["messages"].append({"role": "user", "content": user_message})
    session["query_count"] += 1

    # 履歴を20件に制限
    if len(session["messages"]) > MAX_HISTORY:
        session["messages"] = [session["messages"][0]] + session["messages"][-(MAX_HISTORY-1):]

    # OpenAI呼び出し
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=session["messages"]
    )

    bot_reply = response.choices[0].message.content
    session["messages"].append({"role": "assistant", "content": bot_reply})

    return jsonify({"reply": bot_reply})



@app.route("/reset", methods=["POST"])
def reset():
    session.pop("messages", None)
    session.pop("query_count", None)
    return jsonify({"status": "reset"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
