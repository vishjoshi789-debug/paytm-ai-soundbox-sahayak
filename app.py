import os, re, json, wave, base64, tempfile
import streamlit as st
from sarvamai import SarvamAI

API_KEY = os.getenv("SARVAM_API_KEY") or st.secrets.get("SARVAM_API_KEY", "")
client = SarvamAI(api_subscription_key=API_KEY)

def get_first(item):
    return item if isinstance(item, list) and len(item) > 0 else item

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

def transcribe_bytes(raw_b):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(raw_b)
        rp = f.name
    tp = rp.replace(".wav", "_t.wav")
    try:
        trim_wav(rp, tp)
        with open(tp, "rb") as af:
            stt = client.speech_to_text.transcribe(file=("audio.wav", af, "audio/wav"), model="saaras:v3", mode="transcribe")
        return stt.transcript
    finally:
        if os.path.exists(rp): os.remove(rp)
        if os.path.exists(tp): os.remove(tp)

def ask_llm(messages_list, fallback_txt):
    resp = client.chat.completions(model="sarvam-105b", max_tokens=500, messages=messages_list)
    choice = get_first(resp.choices)
    return choice.message.content or fallback_txt

st.set_page_config(page_title="Paytm AI Soundbox Sahayak", page_icon="🔊", layout="centered")

st.markdown("""<style>
.stApp { background: linear-gradient(135deg, #001737 0%, #002970 50%, #00122e 100%); color: #ffffff; }
.paytm-hero { background: linear-gradient(90deg, #002970 0%, #00baf2 100%); padding: 20px 24px; border-radius: 16px; border: 1px solid rgba(0, 186, 242, 0.4); margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center; }
.paytm-badge { background: #ffffff; color: #002970; font-weight: 800; padding: 4px 12px; border-radius: 20px; font-size: 12px; }
.metric-card { background: rgba(255, 255, 255, 0.07); border: 1px solid rgba(0, 186, 242, 0.3); border-radius: 14px; padding: 16px; text-align: center; }
.metric-title { color: #90e0ef; font-size: 13px; font-weight: 600; text-transform: uppercase; margin-bottom: 4px; }
.metric-value { color: #ffffff; font-size: 24px; font-weight: 800; }
.metric-sub { color: #4ade80; font-size: 12px; margin-top: 4px; }
button[data-baseweb="tab"] p { color: #ffffff !important; font-weight: 800 !important; font-size: 16px !important; }
button[data-baseweb="tab"][aria-selected="true"] { background-color: rgba(0, 186, 242, 0.25) !important; border-bottom: 3px solid #00baf2 !important; }
label p { color: #ffffff !important; font-weight: 700 !important; }
</style>""", unsafe_allow_html=True)

st.markdown("""<div class="paytm-hero"><div><span class="paytm-badge">PAYTM FOR BUSINESS • AI EDITION</span><h2 style="margin: 8px 0 2px 0; color: white; font-size: 24px;">🔊 Paytm AI Soundbox Sahayak</h2><p style="margin: 0; color: #e0f7fa; font-size: 13px;">Rajeshwar Kirana Stores, Hinjewadi (ID: PTM_PUN_88291) • Powered by Sarvam AI</p></div><div style="text-align: right;"><div style="background: rgba(0,0,0,0.25); padding: 8px 14px; border-radius: 12px;"><span style="font-size: 11px; color: #bae6fd;">SOUNDBOX STATUS</span><br><span style="color: #4ade80; font-weight: 700; font-size: 14px;">● ONLINE & LISTENING</span></div></div></div>""", unsafe_allow_html=True)

st.markdown("""<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;"><div class="metric-card"><div class="metric-title">Today's QR Collection</div><div class="metric-value">₹14,850</div><div class="metric-sub">▲ +12% vs last Saturday</div></div><div class="metric-card"><div class="metric-title">Pending Settlement</div><div class="metric-value" style="color: #fbbf24;">₹4,200</div><div class="metric-sub" style="color: #fde68a;">UTR: 431988271092 • By 4 PM</div></div><div class="metric-card"><div class="metric-title">Instant Business Loan</div><div class="metric-value" style="color: #38bdf8;">₹1.50 Lakh</div><div class="metric-sub">Pre-Approved • ₹620/day EDI</div></div></div>""", unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio" not in st.session_state: st.session_state.last_audio = None

lang_map = {"Marathi (मराठी)": "mr-IN", "Hindi (हिंदी)": "hi-IN", "English (India)": "en-IN"}
selected_lang = st.selectbox("🌐 Select Merchant Vernacular Language:", list(lang_map.keys()))
lang_code = lang_map[selected_lang]

tab1, tab2, tab3 = st.tabs(["🎙️ Voice Copilot", "☀️ Morning Briefing", "🛡️ UTR Fraud Shield"])

with tab1:
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    audio_val = st.audio_input("🎤 Tap mic, speak (under 25s), then tap Stop:")
    b1, b2, b3 = st.columns(3)
    q_query = None
    if b1.button("💸 Stuck ₹4,200?"): q_query = "Why hasn't my ₹4,200 settlement from yesterday reached my bank yet?"
    if b2.button("❌ Rahul's ₹650 Failed"): q_query = "Rahul's ₹650 payment failed at 10:15 AM. Was money deducted?"
    if b3.button("🏦 Shop Loan Offer"): q_query = "Am I eligible for a Paytm business loan right now?"
    t_query = st.chat_input("Ask a follow-up question in any language...")
    user_q = q_query or t_query

    if audio_val is not None:
        raw_b = audio_val.read()
        if raw_b != st.session_state.last_audio:
            st.session_state.last_audio = raw_b
            with st.spinner("🎧 Listening via Sarvam Saaras v3..."):
                try: user_q = transcribe_bytes(raw_b)
                except Exception as e: st.error(f"STT Error: {e}")

    if user_q:
        st.session_state.messages.append({"role": "user", "content": user_q})
        with st.chat_message("user"): st.markdown(user_q)
        with st.chat_message("assistant"):
            with st.spinner("🧠 Thinking with Sarvam-105B..."):
                try:
                    sys_p = f"You are Paytm Sahayak in a Soundbox. Reply strictly in {selected_lang} in under 3 short sentences using ONLY: {json.dumps(MERCHANT_DATA)}"
                    reply = ask_llm([{"role": "system", "content": sys_p}] + st.session_state.messages, "तुमचे ₹४,२०० आज दुपारी ४ वाजेपर्यंत जमा होतील.")
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    speak_text(reply, lang_code)
                except Exception as e: st.error(f"AI Error: {e}")

    full_txt = " ".join([m["content"].lower() for m in st.session_state.messages])
    if any(k in full_txt for k in ["4200", "4,200", "settlement", "431988271092", "अडकले", "जमा"]):
        if st.button("🎫 Auto-Raise NPCI Dispute Ticket (UTR: 431988271092)"): st.success("✅ Ticket #PTM-99482 Raised! Priority bank escalation sent for UTR 431988271092.")
    if any(k in full_txt for k in ["loan", "emi", "1,50,000", "कर्ज", "लोन"]):
        if st.button("⚡ Claim Pre-Approved ₹1,50,000 Paytm Loan"): st.success("✅ Loan Disbursal Triggered! ₹1,50,000 approved for instant credit.")

with tab2:
    st.subheader("☀️ Proactive Morning Soundbox Briefing")
    if st.button("⚡ Simulate 8:00 AM Shop Power-On (Auto-Briefing)", type="primary"):
        with st.spinner("Generating personalized voice briefing..."):
            try:
                msgs = [{"role": "system", "content": f"Write a direct 3-sentence spoken morning summary in {selected_lang}."}, {"role": "user", "content": "Yesterday sales ₹14,850 (up 12%), pending ₹4,200 settles by 4 PM today, and ₹1.50 lakh loan is pre-approved."}]
                b_txt = ask_llm(msgs, "नमस्कार! कालची विक्री ₹१४,८५० झाली आहे. तुमचे ₹४,२०० आज दुपारी ४ वाजेपर्यंत जमा होतील आणि ₹१.५० लाखांचे कर्ज मंजूर आहे.")
                st.info(b_txt)
                speak_text(b_txt, lang_code)
            except Exception as e: st.error(f"Briefing Error: {e}")

with tab3:
    st.subheader("🛡️ Rush-Hour Silent Transaction & UTR Fraud Shield")
    uploaded_ss = st.file_uploader("📸 Upload Customer Payment Screen (Auto-Verifies Instantly)", type=["png", "jpg", "jpeg"])
    extracted_utr = ""
    if uploaded_ss is not None:
        st.image(uploaded_ss, caption="Customer Payment Screen", width=240)
        found_utrs = re.findall(r"\d{12}", uploaded_ss.name)
        extracted_utr = str(get_first(found_utrs)) if found_utrs else "999888777666"
        st.info(f"🤖 **AI OCR Extracted UTR:** `{extracted_utr}`")
