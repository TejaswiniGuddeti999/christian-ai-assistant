import streamlit as st
from utils import (
    client, is_blocked, DENOM_CONTEXT,
    chat, generate_image, lookup_verse, extract_verse_ref
)

#  Page config 
st.set_page_config(
    page_title="Christian AI Assistant",
    page_icon="✝️",
    layout="centered"
)

#  Session state 
if "history" not in st.session_state:
    st.session_state.history = []

#  Sidebar 
with st.sidebar:
    st.title("✝️ Christian AI")
    st.caption("Scripture-grounded · Safety-moderated")
    st.divider()

    denomination = st.selectbox("Denomination", list(DENOM_CONTEXT.keys()))

    st.divider()
    st.markdown("**💡 You can ask me to:**")
    st.caption("• Explain theology or doctrine")
    st.caption("• Look up any Bible verse")
    st.caption("• Generate Christian artwork")
    st.caption("• Handle difficult faith questions")

    st.divider()
    if st.button(" Clear conversation"):
        st.session_state.history = []
        st.rerun()

    st.caption("Powered by GPT-4o · bible-api.com · gpt-image-1")

#  API key check 
if not client:
    st.error("No OpenAI API key found. Add OPENAI_API_KEY to your .env file.")
    st.stop()

#  Header 
st.title(" Christian AI Assistant")
st.caption("Ask anything about Christianity — theology, scripture, or request Christian artwork.")

#  Render chat history 
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image":
            st.image(msg["image"], caption=msg.get("caption", ""))
            with st.expander("🔍 View image prompt"):
                st.code(msg["content"])
        else:
            st.markdown(msg["content"])
            if msg.get("verse_verified"):
                st.caption(f"📖 {msg['verse_verified']} — verified via Bible API")

#  Chat input 
user_input = st.chat_input("Ask a question, look up a verse, or say 'generate an image of...'")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.history.append({"role": "user", "content": user_input})

    # Moderation check
    if is_blocked(user_input):
        reply = "I'm sorry, I can't help with that request. I'm here to support faith and spiritual growth — not produce content contrary to Christian values. Is there something else I can help you with? 🙏"
        with st.chat_message("assistant"):
            st.warning(reply)
        st.session_state.history.append({"role": "assistant", "content": reply})
        st.stop()

    # Get GPT-4o response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = chat(user_input, denomination, st.session_state.history[:-1])

        # Split text and image parts
        image_prompt = None
        text_reply = reply

        if "IMAGE_REQUEST:" in reply:
            parts = reply.split("IMAGE_REQUEST:")
            text_reply = parts[0].strip()
            image_prompt = parts[1].strip()

        # Show text response
        if text_reply:
            verse_ref = extract_verse_ref(text_reply)
            verse_verified = None
            if verse_ref:
                verse_data = lookup_verse(verse_ref)
                if verse_data:
                    verse_verified = verse_data["reference"]
            st.markdown(text_reply)
            if verse_verified:
                st.caption(f" {verse_verified} — verified via Bible API")
            st.session_state.history.append({
                "role": "assistant",
                "content": text_reply,
                "verse_verified": verse_verified
            })

        # Generate image if requested
        if image_prompt:
            st.info(" Generating image...")
            try:
                image = generate_image(image_prompt)
                st.image(image, caption="Generated Christian artwork")
                with st.expander("🔍 View image prompt"):
                    st.code(image_prompt)
                st.session_state.history.append({
                    "role": "assistant",
                    "type": "image",
                    "content": image_prompt,
                    "image": image,
                    "caption": "Generated Christian artwork"
                })
            except Exception as e:
                st.error(f"Image generation failed: {e}")