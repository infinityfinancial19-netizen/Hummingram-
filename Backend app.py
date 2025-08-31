from flask import Flask, jsonify, request
import hashlib
import os

app = Flask(__name__)

# Environment placeholders
DATABASE_URL = os.getenv("DATABASE_URL", "YOUR_SUPABASE_URL_HERE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_KEY_HERE")

users = []
posts = []

def generate_post_hash(post):
    post_string = f"{post.get('author','')}{post.get('content','')}"
    return hashlib.sha256(post_string.encode()).hexdigest()

def generate_ai_caption(content):
    # Placeholder for AI caption
    return f"AI Caption for: {content[:50]}..."

@app.route("/")
def home():
    return "HumminGgram Backend Running"

@app.route("/users", methods=["GET","POST"])
def manage_users():
    if request.method == "POST":
        data = request.get_json() or {}
        users.append({"name": data.get("name",""), "bio": data.get("bio","")})
        return jsonify({"status":"user added"}), 201
    return jsonify(users)

@app.route("/posts", methods=["GET","POST"])
def manage_posts():
    if request.method == "POST":
        data = request.get_json() or {}
        data['hash'] = generate_post_hash(data)
        data['caption'] = generate_ai_caption(data.get("content",""))
        data['media_url'] = data.get("media_url","")
        posts.append({"author": data.get("author",""), "content": data.get("content",""),
                      "caption":data['caption'], "hash":data['hash'], "media_url":data['media_url']})
        return jsonify({"status":"post added","hash":data['hash']}), 201
    return jsonify(posts)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
