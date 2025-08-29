import os
import shutil

base_path = "HumminGgram"
os.makedirs(base_path, exist_ok=True)

# ---------- Backend ----------
backend_path = os.path.join(base_path, "backend")
os.makedirs(backend_path, exist_ok=True)

backend_files = {
    "app.py": """from flask import Flask, jsonify, request
import os
import psycopg2
import hashlib
import openai

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

conn = None
if DATABASE_URL:
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    except Exception as e:
        print("Database connection failed:", e)

def generate_caption(content):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"Generate a caption for: {content}"}]
        )
        return response.choices[0].message.get("content", "")
    except Exception as e:
        print("OpenAI API error:", e)
        return ""

def generate_post_hash(post):
    post_string = f"{post.get('author','')}{post.get('content','')}"
    return hashlib.sha256(post_string.encode()).hexdigest()

@app.route('/')
def home():
    return "HumminGgram Backend Running"

@app.route('/users', methods=['GET','POST'])
def users():
    if request.method == 'POST':
        data = request.get_json() or {}
        if conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (name, bio) VALUES (%s,%s)",
                    (data.get('name',''), data.get('bio',''))
                )
                conn.commit()
        return jsonify({"status": "user added"}), 201

    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name, bio FROM users")
            users = [{"name": row[0], "bio": row[1]} for row in cur.fetchall()]
        return jsonify(users)
    return jsonify([])

@app.route('/posts', methods=['GET','POST'])
def posts():
    if request.method == 'POST':
        data = request.get_json() or {}
        data['caption'] = generate_caption(data.get('content',''))
        data['hash'] = generate_post_hash(data)
        if conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO posts (author, content, caption, hash) VALUES (%s,%s,%s,%s)",
                    (data.get('author',''), data.get('content',''), data['caption'], data['hash'])
                )
                conn.commit()
        return jsonify({'status':'post added', 'hash': data['hash']}), 201

    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT author, content, caption, hash FROM posts")
            posts = [
                {"author": row[0], "content": row[1], "caption": row[2], "hash": row[3]}
                for row in cur.fetchall()
            ]
        return jsonify(posts)
    return jsonify([])

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)""",

    "requirements.txt": """flask
psycopg2-binary
gunicorn
waitress
openai""",

    "Dockerfile": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]""",

    "runtime.txt": "python-3.11.6",

    "init.sql": """CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    bio TEXT
);

CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    author TEXT NOT NULL,
    content TEXT NOT NULL,
    caption TEXT,
    hash TEXT UNIQUE
);"""
}

for filename, content in backend_files.items():
    with open(os.path.join(backend_path, filename), "w") as f:
        f.write(content)

# ---------- Frontend ----------
frontend_path = os.path.join(base_path, "frontend")
os.makedirs(frontend_path, exist_ok=True)

frontend_files = {
    "frontend.py": """import streamlit as st
import requests

BACKEND_URL = "https://your-backend-url.onrender.com"

st.set_page_config(page_title="HumminGgram", page_icon="🎵", layout="centered")
st.title("HumminGgram - Social Media Prototype")

menu = ["Home", "Create User", "Create Post", "View Users", "View Posts"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Home":
    st.subheader("Welcome to HumminGgram 🎶")
    st.write("Interact with users and posts in real-time.")

elif choice == "Create User":
    name = st.text_input("Name")
    bio = st.text_input("Bio")
    if st.button("Add User"):
        res = requests.post(f"{BACKEND_URL}/users", json={"name": name, "bio": bio})
        if res.status_code == 201:
            st.success("User added!")

elif choice == "Create Post":
    author = st.text_input("Author")
    content = st.text_area("Content")
    if st.button("Add Post"):
        res = requests.post(f"{BACKEND_URL}/posts", json={"author": author, "content": content})
        if res.status_code == 201:
            st.success(f"Post added with hash: {res.json().get('hash')}")

elif choice == "View Users":
    res = requests.get(f"{BACKEND_URL}/users")
    if res.status_code == 200:
        st.json(res.json())

elif choice == "View Posts":
    res = requests.get(f"{BACKEND_URL}/posts")
    if res.status_code == 200:
        posts_data = res.json()
        for p in posts_data:
            st.markdown(f"**Author:** {p.get('author','')}\n**Content:** {p.get('content','')}\n**Caption:** {p.get('caption','')}\n**Hash:** {p.get('hash','')}")
""",

    "requirements.txt": """streamlit
requests"""
}

for filename, content in frontend_files.items():
    with open(os.path.join(frontend_path, filename), "w") as f:
        f.write(content)

# ---------- README.md ----------
readme_content = """# HumminGgram - AI + AR Social Media Prototype

## Structure

- backend/: Flask backend with OpenAI captioning, Postgres DB.
- frontend/: Streamlit frontend for users and posts.
- init.sql: DB schema initialization.
- Dockerfile: Backend container for Render deployment.

## Deployment

### Backend (Render)
1. Create a free Postgres DB on Render.
2. Deploy the backend folder using Render (detect Dockerfile automatically).
3. Set environment variables:
   - `DATABASE_URL` = Render Postgres URL
   - `OPENAI_API_KEY` = Your OpenAI key
4. Initialize DB:
   - Connect to the Postgres DB using a client.
   - Run `init.sql` to create tables.
5. Backend URL will be used in frontend.

### Frontend (Streamlit Cloud)
1. Go to [Streamlit Cloud](https://share.streamlit.io) and create a new app.
2. Connect the GitHub repo containing `frontend/`.
3. Set main file to `frontend/frontend.py`.
4. Add secret:
   - `BACKEND_URL` = URL of deployed backend
5. Deploy → Live frontend ready.

Enjoy your boundless HumminGgram experience! 🌸💝
"""

with open(os.path.join(base_path, "README.md"), "w") as f:
    f.write(readme_content)

# ---------- Create ZIP ----------
zip_file_path = "/mnt/data/HumminGgram.zip"
shutil.make_archive(zip_file_path.replace(".zip",""), 'zip', base_path)

print(f"HumminGgram project folder created and zipped as {zip_file_path} successfully!")
