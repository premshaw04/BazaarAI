import os
import tempfile

import streamlit as st

from shopping_agent import agent

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="AI Shopping Assistant", page_icon="🛒", layout="wide")

st.title("🛒 AI Shopping Assistant")
st.caption("Tell me what you want — I'll search, rate, and order the best match for you.")

# ---------------------------------------------------------------------------
# Sidebar — shop by image & settings
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Shop by Image")
    st.caption("Upload a photo of a product and I'll find similar items in our store.")

    uploaded_file = st.file_uploader(
        "Upload product image", type=["jpg", "jpeg", "png", "webp"]
    )

    if uploaded_file:
        st.image(uploaded_file, use_container_width=True)

    if uploaded_file and st.button("Find similar products", use_container_width=True):
        if not os.environ.get("GROQ_API_KEY"):
            st.error("Please enter a Groq API Key below first.")
        else:
            suffix = os.path.splitext(uploaded_file.name)[1] or ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getvalue())
                image_path = tmp.name

            prompt = f"I uploaded a product image. Please analyze it and find similar products in the store. Image path: {image_path}"
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.pending_image = uploaded_file.name
            st.rerun()

    st.divider()
    st.header("Settings")
    current_key = os.environ.get("GROQ_API_KEY", "")
    api_key_input = st.text_input(
        "Groq API Key",
        value=current_key,
        type="password",
        placeholder="gsk_...",
        help="Get your free API key at console.groq.com",
    )
    if api_key_input and api_key_input != current_key:
        os.environ["GROQ_API_KEY"] = api_key_input.strip()
        st.success("API key updated!")

    if not os.environ.get("GROQ_API_KEY"):
        st.info("💡 A Groq API key is required. Enter it above or add it to `.env` as `GROQ_API_KEY`.")

    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        if "pending_image" in st.session_state:
            del st.session_state.pending_image
        st.rerun()

# ---------------------------------------------------------------------------
# Chat state
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render history — show a friendlier label for image-search messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user" and msg["content"].startswith("I uploaded a product image"):
            filename = msg["content"].split("Image path:")[-1].strip()
            st.markdown(f"Searching by image: **{os.path.basename(filename)}**")
        else:
            st.markdown(msg["content"].replace("$", r"\$"))

# ---------------------------------------------------------------------------
# Run agent if there's an unprocessed message (image upload triggers this)
# ---------------------------------------------------------------------------
if (
    st.session_state.messages
    and st.session_state.messages[-1]["role"] == "user"
    and "pending_image" in st.session_state
):
    if not os.environ.get("GROQ_API_KEY"):
        st.error("⚠️ Please provide a Groq API key in the sidebar before searching.")
    else:
        with st.chat_message("assistant"):
            with st.spinner("Analyzing image and searching…"):
                try:
                    result = agent.invoke({"messages": st.session_state.messages})
                    response = result["messages"][-1].content.replace("`", "")
                except Exception as e:
                    response = f"An error occurred: {e}"
            st.markdown(response.replace("$", r"\$"))

        st.session_state.messages.append({"role": "assistant", "content": response})
        del st.session_state.pending_image
        st.rerun()

# ---------------------------------------------------------------------------
# Text input
# ---------------------------------------------------------------------------
if prompt := st.chat_input("e.g. I want organic honey under $15 with 4+ rating"):
    if not os.environ.get("GROQ_API_KEY"):
        st.error("⚠️ Please enter your Groq API Key in the sidebar to chat.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    result = agent.invoke({"messages": st.session_state.messages})
                    response = result["messages"][-1].content.replace("`", "")
                except Exception as e:
                    response = f"An error occurred: {e}"
            st.markdown(response.replace("$", r"\$"))

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
