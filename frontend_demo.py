
import streamlit as st
import requests
from PIL import Image
import io

BACKEND_URL = "http://127.0.0.1:5000"

st.title("HumminGgram Demo with AI + Media")

menu = ["Home","Create User","Create Post","View Users","View Posts"]
choice = st.sidebar.selectbox("Menu", menu)

if choice=="Home":
    st.subheader("Welcome to HumminGgram Demo v1 with AI + Media")

elif choice=="Create User":
    name = st.text_input("Name")
    bio = st.text_input("Bio")
    if st.button("Add User"):
        res = requests.post(f"{BACKEND_URL}/users", json={"name":name,"bio":bio})
        st.success(res.json().get("status","User added"))

elif choice=="Create Post":
    author = st.text_input("Author")
    content = st.text_area("Content")
    media_url = st.text_input("Media URL (Google Drive link)")
    if st.button("Add Post"):
        res = requests.post(f"{BACKEND_URL}/posts", json={"author":author,"content":content,"media_url":media_url})
        st.success(f"Post added with hash: {res.json().get('hash','')}")

elif choice=="View Users":
    res = requests.get(f"{BACKEND_URL}/users")
    st.json(res.json())

elif choice=="View Posts":
    res = requests.get(f"{BACKEND_URL}/posts")
    posts = res.json()
    for p in posts:
        st.markdown(f"**Author:** {p.get('author','')}")
        st.markdown(f"**Content:** {p.get('content','')}")
        st.markdown(f"**Caption:** {p.get('caption','')}")
        st.markdown(f"**Hash:** {p.get('hash','')}")
        if p.get("media_url"):
            st.video(p.get("media_url"))
