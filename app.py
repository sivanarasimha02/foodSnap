import json
import os
import streamlit as st
from google import genai
from google.genai import types

# Optional Twilio import for WhatsApp messaging
try:
    from twilio.rest import Client as TwilioClient
except ImportError:
    TwilioClient = None

# Import prompts safely with fallback
import prompts

SYSTEM_PROMPT = getattr(
    prompts,
    "SYSTEM_PROMPT",
    "You are FoodSnap AI, an intelligent AI vision assistant that analyzes food images."
)

WELCOME_MESSAGE_TEMPLATE = getattr(
    prompts,
    "WELCOME_MESSAGE_TEMPLATE",
    getattr(
        prompts,
        "WELCONE_MESSAGE_TEMPLATE",
        "👋 Welcome to FoodSnap AI! 🍎\nUpload or capture a food image and let me analyze it."
    )
)

SUMMARY_PROMPTS = getattr(
    prompts,
    "SUMMARY_PROMPTS",
    getattr(
        prompts,
        "SUMMARY_REQUEST_PROMPT",
        "Analyze the provided food image and summarize the result in 3–4 concise lines."
    )
)

# --- Page Configuration ---
st.set_page_config(
    page_title="FoodSnap AI - Vision Chatbot 🥗",
    page_icon="🍎",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Custom Styling (Hides sidebar completely) ---
st.markdown("""
<style>
    /* Hide sidebar and toggle button completely */
    [data-testid="stSidebar"], [data-testid="stSidebarCollapseButton"], section[data-testid="stSidebar"] {
        display: none !important;
    }
    .badge-chip {
        display: inline-block;
        padding: 4px 10px;
        margin: 2px 4px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        background-color: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
    }
    .stChatInput {
        bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


# --- Helper: Safe Secret Retrieval ---
def get_secret(key: str, default: str = "") -> str:
    """Retrieve secrets safely from st.secrets or environment."""
    try:
        if key in st.secrets:
            val = st.secrets[key]
            if val and val not in ("YOUR_API_KEY_HERE", "YOUR_TWILIO_SID"):
                return str(val).strip()
    except Exception:
        pass
    return os.environ.get(key, default).strip()


GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
TWILIO_ACCOUNT_SID = get_secret("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = get_secret("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = get_secret("TWILIO_WHATSAPP_FROM", "+14155238886")
TWILIO_CONTENT_SID = get_secret("TWILIO_CONTENT_SID")

# Vision Model ID
MODEL_NAME = get_secret("GEMINI_MODEL", "gemini-2.5-flash")


# --- Client Initializations ---
@st.cache_resource
def get_gemini_client(api_key: str):
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


@st.cache_resource
def get_twilio_client(account_sid: str, auth_token: str):
    if TwilioClient and account_sid and auth_token:
        try:
            return TwilioClient(account_sid, auth_token)
        except Exception:
            return None
    return None


gemini_client = get_gemini_client(GEMINI_API_KEY) if GEMINI_API_KEY else None
twilio_client = get_twilio_client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN) else None


# --- Chat & Messaging Helper Functions ---
def render_message(message):
    """Renders text or image messages in the Streamlit chat stream."""
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.markdown(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"], width="stretch")


def add_message(role, kind, content):
    """Adds a message to session history and renders it."""
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])


def ask_gemini(parts):
    """Sends multimodal parts (images and/or text) to the Gemini Chat session."""
    if "chat" not in st.session_state or st.session_state.chat is None:
        if not gemini_client:
            return "❌ Gemini API Key not found. Please set `GEMINI_API_KEY` in `.streamlit/secrets.toml`."
        st.session_state.chat = gemini_client.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        )
    try:
        response = st.session_state.chat.send_message(parts)
        return response.text
    except Exception as error:
        return f"Sorry, something went wrong: {error}"


def clean_whatsapp_text(text):
    if not text:
        return "No nutrition summary available."
    text = " ".join(text.split())
    return text[:1500] + "..." if len(text) > 1500 else text


def send_whatsapp(to_number, user_name, summary):
    """Sends WhatsApp summary via Twilio if configured."""
    if not twilio_client:
        return False, "Twilio is not configured."
    try:
        if TWILIO_CONTENT_SID:
            content_variables = json.dumps(
                {"1": user_name, "2": clean_whatsapp_text(summary)}, ensure_ascii=False
            )
            message = twilio_client.messages.create(
                from_=TWILIO_WHATSAPP_FROM,
                to=f"whatsapp:{to_number}",
                content_sid=TWILIO_CONTENT_SID,
                content_variables=content_variables,
            )
        else:
            message = twilio_client.messages.create(
                from_=TWILIO_WHATSAPP_FROM,
                to=f"whatsapp:{to_number}",
                body=f"🍎 *FoodSnap Daily Summary for {user_name}*\n\n{summary}",
            )
        return True, message.sid
    except Exception as error:
        return False, str(error)


# ==========================================
# STEP 1: ONBOARDING VIEW
# ==========================================
if "onboarded" not in st.session_state:
    st.title("🍎 FoodSnap AI")
    st.caption("AI Vision Chatbot for Nutrition, Calories & Meal Tracking")

    st.markdown("""
    <div>
        <span class="badge-chip">⚡ Photo Calorie Estimation</span>
        <span class="badge-chip">🥗 Macro Breakdown</span>
        <span class="badge-chip">🍳 Recipe Insights</span>
        <span class="badge-chip">📲 WhatsApp Daily Summary</span>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    with st.form("onboarding_form"):
        st.subheader("👋 Welcome! Let's get started")
        
        name = st.text_input("Your Name", placeholder="e.g. Alex")
        whatsapp_number = st.text_input(
            "WhatsApp Number (with country code)",
            placeholder="+1XXXXXXXXXX or +91XXXXXXXXXX",
            help="Your daily nutrition summaries can be texted to this number.",
        )
            
        submitted = st.form_submit_button("Start FoodSnap 🚀", type="primary", width="stretch")

    if submitted:
        if not name.strip() or not whatsapp_number.strip():
            st.warning("Please fill in both your name and WhatsApp number.")
        else:
            st.session_state.name = name.strip()
            st.session_state.whatsapp_number = whatsapp_number.strip()
            
            if gemini_client:
                st.session_state.chat = gemini_client.chats.create(
                    model=MODEL_NAME,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                )
            st.session_state.messages = []
            st.session_state.onboarded = True
            st.rerun()
    st.stop()


# ==========================================
# STEP 2: AI VISION CHAT INTERFACE
# ==========================================
header_col, action_col1, action_col2 = st.columns([5, 3, 2], vertical_alignment="center")

with header_col:
    st.title("🥗 FoodSnap AI")

with action_col1:
    send_disabled = len(st.session_state.get("messages", [])) < 2
    if st.button("📤 WhatsApp Summary", disabled=send_disabled, width="stretch", type="secondary"):
        with st.spinner("Generating daily nutrition summary..."):
            summary = ask_gemini([SUMMARY_PROMPTS])
        
        if twilio_client:
            success, info = send_whatsapp(st.session_state.whatsapp_number, st.session_state.name, summary)
            if success:
                st.success("Sent! Check your WhatsApp 📲")
            else:
                st.error(f"WhatsApp send failed: {info}")
        else:
            # Fallback preview dialog if Twilio keys are not configured
            st.info("💡 Twilio not connected. Here is your daily summary:")
            st.code(summary, language="markdown")

with action_col2:
    if st.button("🔄 Reset", width="stretch", help="Restart chat session"):
        for key in ["onboarded", "name", "whatsapp_number", "chat", "messages"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

st.caption(f"Logged in as **{st.session_state.name}** • Summaries go to `{st.session_state.whatsapp_number}`")

# Render existing chat history or initial welcome message
if not st.session_state.get("messages"):
    try:
        welcome_txt = WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name)
    except Exception:
        welcome_txt = WELCOME_MESSAGE_TEMPLATE
    add_message("assistant", "text", welcome_txt)
else:
    for message in st.session_state.messages:
        render_message(message)

# Multimodal Chat Input (accepting text + image attachments)
user_input = st.chat_input(
    "Ask a question or attach a photo of your food...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "webp"],
)

if user_input:
    # Extract attached files and prompt text
    files = getattr(user_input, "files", None) or []
    photo = files[0] if files else None
    text = getattr(user_input, "text", "") or (str(user_input) if isinstance(user_input, str) else "")
    parts = []

    # If an image is attached, append its bytes and render in chat
    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type or "image/jpeg"))
    
    # If text is entered, append and render in chat
    if text and text.strip():
        add_message("user", "text", text.strip())
        parts.append(text.strip())
    elif photo is not None:
        # Default prompt when only an image is sent
        default_prompt = "Identify this food, estimate the portion size, total calories, and macronutrients (protein, carbs, fats), and share helpful nutrition insights."
        parts.append(default_prompt)

    # Process with Gemini Vision Chat
    if parts:
        with st.spinner("Analyzing food photo and crunching the numbers..."):
            answer = ask_gemini(parts)
        add_message("assistant", "text", answer)
