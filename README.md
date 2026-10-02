# 🥗 FoodSnap AI — Multimodal Nutrition Vision Chatbot

**FoodSnap AI** is an intelligent, multimodal food recognition and dietary vision assistant powered by **Google Gemini Vision** and **Streamlit**. Simply snap or upload a photo of any dish or snack, and FoodSnap AI will identify the ingredients, estimate portions, calculate calories and macronutrients, and text you a daily summary on WhatsApp!

---

## ✨ Features

- **📸 Multimodal Food Vision**: Snap or upload photos (`JPG`, `PNG`, `WEBP`) of meals directly in the chat.
- **🔥 Instant Calorie & Macro Estimation**: Breaks down total calories, protein, carbohydrates, fats, and fiber with realistic portion approximations.
- **💬 Conversational Nutrition Coach**: Ask follow-up questions about ingredients, healthy substitutes, recipes, or glycemic impact.
- **📲 WhatsApp Daily Summary**: 1-click summary generator that sends formatted daily intake updates straight to your WhatsApp via Twilio.
- **📱 Clean, Responsive UI**: Centered single-column design with smooth chat stream, photo attachments, and session management.

---

## 🛠️ Tech Stack

- **AI & Vision Model**: [Google GenAI SDK](https://github.com/google-gemini/google-genai) (`gemini-2.5-flash`)
- **Frontend / Framework**: [Streamlit](https://streamlit.io/)
- **Messaging API**: [Twilio REST API](https://www.twilio.com/docs/whatsapp) (WhatsApp Messaging)
- **Language**: Python 3.10+

---

## 📁 Project Structure

```text
foodSnap/
├── app.py                     # Main Streamlit vision chatbot application
├── prompts.py                 # System prompts, welcome templates & summary formatters
├── requirements.txt           # Python package dependencies
├── .streamlit/
│   ├── config.toml            # Streamlit server & browser configuration
│   └── secrets.toml           # API keys & Twilio configuration
└── README.md                  # Project documentation
```

---

## 🚀 Quickstart Guide

### 1. Clone & Set Up Virtual Environment

```bash
# Clone repository
git clone https://github.com/your-username/foodSnap.git
cd foodSnap

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Create or edit `.streamlit/secrets.toml` in the project root:

```toml
# Google Gemini API Key (https://aistudio.google.com)
GEMINI_API_KEY = "your_gemini_api_key_here"

# Optional: Twilio WhatsApp Credentials (https://console.twilio.com)
TWILIO_ACCOUNT_SID = "your_twilio_account_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_WHATSAPP_FROM = "+14155238886"  # Or your Twilio WhatsApp sender number
TWILIO_CONTENT_SID = ""                # Optional Twilio content template SID
```

### 4. Run the Application

```bash
streamlit run app.py
```

Open **`http://localhost:8501`** in your browser.

---

## ⚙️ Configuration Reference

| Variable | Description | Required |
| :--- | :--- | :---: |
| `GEMINI_API_KEY` | Google Gemini API Key from Google AI Studio | **Yes** |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID for WhatsApp messaging | Optional |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token for WhatsApp authentication | Optional |
| `TWILIO_WHATSAPP_FROM` | Twilio WhatsApp sender number (e.g. `+14155238886`) | Optional |
| `TWILIO_CONTENT_SID` | Twilio Content Template SID (if using approved templates) | Optional |

> 💡 **Note:** If Twilio is not configured, the app will still generate your daily summary and display it in a copy-friendly code block inside the app.

---

## 📖 How to Use

1. **Onboarding**: Enter your Name and WhatsApp phone number (with country code).
2. **Snap or Upload**: Click the 📎 attachment icon in the chat input and select/capture a food photo.
3. **Analyze**: Gemini Vision identifies the meal, breaks down estimated calories and macros, and highlights key nutritional benefits.
4. **Chat & Inquire**: Ask follow-up questions like:
   - *"How can I make this lower in sodium?"*
   - *"Is this meal keto-friendly?"*
   - *"What's a good high-protein side to pair with this?"*
5. **Send Summary**: Click **📤 WhatsApp Summary** in the header to receive your daily food intake breakdown.

---

## ⚠️ Disclaimer

Nutritional values, calorie counts, and portion sizes provided by FoodSnap AI are AI-generated estimations based on visual cues. They are intended for educational and general tracking purposes and should not replace professional medical or clinical dietary advice.
# foodSnap
