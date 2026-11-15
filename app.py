import os, re, json, wave, base64, tempfile
import streamlit as st
from sarvamai import SarvamAI

# 1. Load Sarvam API Key securely from Streamlit Secrets or Environment
API_KEY = os.getenv("SARVAM_API_KEY") or st.secrets.get("SARVAM_API_KEY", "")
client = SarvamAI(api_subscription_key=API_KEY)

# 2. Safe List Extractor
def get_first(item):
    return item if isinstance(item, list) and len(item) > 0 else item

# 3. Mock Paytm Merchant Profile (Pune Kirana Store)
MERCHANT_DATA = {
    "merchant_name": "Rajeshwar Kirana & General Stores, Hinjewadi",
    "merchant_id": "PTM_PUN_88291",
    "todays_collection": "₹14,850 across 62 UPI transactions",
    "yesterday_comparison": "+12% higher than last Saturday",
    "pending_settlement": {
        "amount": "₹4,200",
        "date": "Yesterday (14 Nov)",
        "status": "Delayed due to NPCI partner bank maintenance",
        "expected_credit": "Today by 4:00 PM IST",
        "utr_number": "431988271092"
    },
    "recent_verified_utrs": {
        "631900112233": {"amount": "₹1,250", "customer": "Sneha K.", "time": "11:10 AM"},
        "631900445566": {"amount": "₹340", "customer": "Amit V.", "time": "10:48 AM"}
    },
    "failed_transactions": [
        {"time": "10:15 AM today", "amount": "₹650", "customer_upi": "rahul.p@okaxis", "reason": "Bank timeout (Error U30). Money not deducted."}
    ],
    "loan_eligibility": {
        "eligible": True,
        "pre_approved_amount": "₹1,50,000",
        "daily_deduction_edi": "₹620/day",
        "interest_rate": "1.25% per month"
    }
}

def trim_wav(in_p, out_p, max_s=25):
    with wave.open(in_p, "rb") as wf:
        p = wf.getparams()
        frames = wf.readframes(min(wf.getnframes(), int(wf.getframerate() * max_s)))
    with wave.open(out_p, "wb") as owf:
        owf.setparams(p)
        owf.writeframes(frames)

def speak_text(txt, l_code):
    tts = client.text_to_speech.convert(text=txt, language_code=l_code, speaker="shubh", model="bulbul:v3")
    raw_audio = get_first(tts.audios)
    st.audio(base64.b64decode(raw_audio), format="audio/wav", autoplay=True)

# 4. Page Setup & Custom Paytm Flagship CSS
st.set_page_config(page_title="Paytm AI Soundbox Sahayak", page_icon="🔊", layout="centered")

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #001737 0%, #002970 50%, #00122e 100%);
        color: #ffffff;
    }
    .paytm-hero {
        background: linear-gradient(90deg, #002970 0%, #00baf2 100%);
        padding: 20px 24px;
        border-radius: 16px;
        border: 1px solid rgba(0, 186, 242, 0.4);
        box-shadow: 0 8px 32px rgba(0, 186, 242, 0.25);
        margin-bottom: 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .paytm-badge {
        background: #ffffff;
        color: #002970;
        font-weight: 800;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        letter-spacing: 0.5px;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 186, 242, 0.3);
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .metric-title {
        color: #90e0ef;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .metric-value {
        color: #ffffff;
        font-size: 24px;
        font-weight: 800;
    }
    .metric-sub {
        color: #4ade80;
        font-size: 12px;
        margin-top: 4px;
    }
    .soundbox-card {
        background: linear-gradient(145deg, #0a1f44, #051024);
        border: 2px solid #00baf2;
        border-radius: 18px;
        padding: 14px 20px;
        margin: 12px 0 18px 0;
        box-shadow: 0 0 20px rgba(0, 186, 242, 0.35);
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .pulse-dot {
        height: 14px;
        width: 14px;
        background-color: #00baf2;
        border-radius: 50%;
        box-shadow: 0 0 12px #00baf2, 0 0 24px #00baf2;
        display: inline-block;
    }
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        border: 1px solid #00baf2;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 14px rgba(0, 186, 242, 0.4);
    }
    button[data-baseweb="tab"] p {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 16px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(0, 186, 242, 0.25) !important;
        border-radius: 10px 10px 0 0 !important;
        border-bottom: 3px solid #00baf2 !important;
    }
    label p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="paytm-hero">
    <div>
        <span class="paytm-badge">PAYTM FOR BUSINESS • AI EDITION</span>
        <h2 style="margin: 8px 0 2px 0; color: white; font-size: 24px;">🔊 Paytm AI Soundbox Sahayak</h2>
        <p style="margin: 0; color: #e0f7fa; font-size: 13px;">Rajeshwar Kirana Stores, Hinjewadi (ID: PTM_PUN_88291) • Powered by Sarvam AI</p>
    </div>
    <div style="text-align: right;">
        <div style="background: rgba(0,0,0,0.25); padding: 8px 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.2);">
            <span style="font-size: 11px; color: #bae6fd;">SOUNDBOX STATUS</span><br>
            <span style="color: #4ade80; font-weight: 700; font-size: 14px;">● ONLINE & LISTENING</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;">
    <div class="metric-card">
        <div class="metric-title">Today's QR Collection</div>
        <div class="metric-value">₹14,850</div>
        <div class="metric-sub">▲ +12% vs last Saturday</div>
    </div>
    <div class="metric-card">
        <div class="metric-title">Pending Settlement</div>
        <div class="metric-value" style="color: #fbbf24;">₹4,200</div>
        <div class="metric-sub" style="color: #fde68a;">UTR: 431988271092 • By 4 PM</div>
    </div>
    <div class="metric-card">
        <div class="metric-title">Instant Business Loan</div>
        <div class="metric-value" style="color: #38bdf8;">₹1.50 Lakh</div>
        <div class="metric-sub">Pre-Approved • ₹620/day EDI</div>
    </div>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

lang_map = {"Marathi (मराठी)": "mr-IN", "Hindi (हिंदी)": "hi-IN", "English (India)": "en-IN"}
selected_lang = st.selectbox("🌐 Select Merchant Vernacular Language:", list(lang_map.keys()))
lang_code = lang_map[selected_lang]

st.markdown(f"""
<div class="soundbox-card">
    <span class="pulse-dot"></span>
    <div>
        <div style="font-weight: 700; font-size: 15px; color: #38bdf8;">Paytm Smart Soundbox Pro • Active Mode: {selected_lang}</div>
        <div style="font-size: 12px; color: #cbd5e1;">Tap microphone below or use one-tap merchant shortcuts for instant vernacular voice resolution.</div>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🎙️ Voice Copilot", "☀️ Morning Briefing", "🛡️ UTR Fraud Shield"])

with tab1:
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    audio_val = st.audio_input("🎤 Tap mic, speak (under 25s), then tap Stop:")
    b1, b2, b3 = st.columns(3)
    q_query = None
    if b1.button("💸 Stuck ₹4,200?"):
        q_query = "Why hasn't my ₹4,200 settlement from yesterday reached my bank yet?"
    if b2.button("❌ Rahul's ₹650 Failed"):
        q_query = "Rahul's ₹650 payment failed at 10:15 AM. Was money deducted?"
    if b3.button("🏦 Shop Loan Offer"):
        q_query = "Am I eligible for a Paytm business loan right now?"

    t_query = st.chat_input("Ask a follow-up question in any language...")
    user_q = None

    if audio_val is not None:
        raw_b = audio_val.read()
        if raw_b != st.session_state.last_audio:
            st.session_state.last_audio = raw_b
            with st.spinner("🎧 Listening via Sarvam Saaras v3..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                    f.write(raw_b)
                    rp = f.name
                tp = rp.replace(".wav", "_t.wav")
                try:
                    trim_wav(rp, tp)
                    with open(tp, "rb") as af:
                        stt = client.speech_to_text.transcribe(
                            file=("audio.wav", af, "audio/wav"),
                            model="saaras:v3",
                            mode="transcribe"
                        )
                    user_q = stt.transcript
                except Exception as e:
                    st.error(f"STT Error: {e}")
                finally:
                    for x in [rp, tp]:
                        if os.path.exists(x):
                            os.remove(x)
    elif q_query:
        user_q = q_query
    elif t_query:
        user_q = t_query

    if user_q:
        st.session_state.messages.append({"role": "user", "content": user_q})
        with st.chat_message("user"):
            st.markdown(user_q)
        with st.chat_message("assistant"):
            with st.spinner("🧠 Thinking with Sarvam-105B & generating Soundbox audio..."):
                try:
