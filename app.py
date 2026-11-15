import os
import json
import wave
import base64
import tempfile
import streamlit as st
from sarvamai import SarvamAI

# 1. PASTE YOUR SARVAM API KEY BELOW
API_KEY = os.getenv("SARVAM_API_KEY") or st.secrets.get("SARVAM_API_KEY", "")

client = SarvamAI(api_subscription_key=API_KEY)

# 2. Mock Paytm Merchant Profile (Pune Kirana Store)
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
        "631900112233": {
            "amount": "₹1,250",
            "customer": "Sneha K.",
            "time": "11:10 AM",
            "status": "VERIFIED_SETTLED"
        },
        "631900445566": {
            "amount": "₹340",
            "customer": "Amit V.",
            "time": "10:48 AM",
            "status": "VERIFIED_SETTLED"
        }
    },
    "failed_transactions": [
        {
            "time": "10:15 AM today",
            "amount": "₹650",
            "customer_upi": "rahul.p@okaxis",
            "reason": "Customer bank server timeout (Error U30). Money not deducted from customer."
        }
    ],
    "loan_eligibility": {
        "eligible": True,
        "pre_approved_amount": "₹1,50,000",
        "daily_deduction_edi": "₹620/day from daily QR settlements",
        "interest_rate": "1.25% per month"
    }
}

def trim_wav_to_25s(input_path, output_path, max_seconds=25):
    with wave.open(input_path, "rb") as wf:
        params = wf.getparams()
        max_frames = int(wf.getframerate() * max_seconds)
        frames = wf.readframes(min(wf.getnframes(), max_frames))
    with wave.open(output_path, "wb") as out_wf:
        out_wf.setparams(params)
        out_wf.writeframes(frames)

def speak_text(text_to_speak, lang_code):
    tts_resp = client.text_to_speech.convert(
        text=text_to_speak,
        language_code=lang_code,
        speaker="shubh",
        model="bulbul:v3"
    )
    audio_bytes = base64.b64decode(tts_resp.audios)
    st.audio(audio_bytes, format="audio/wav", autoplay=True)

st.set_page_config(page_title="Paytm Merchant Sahayak", page_icon="🎙️", layout="centered")
st.title("🎙️ Paytm AI Soundbox & Merchant Sahayak")
st.caption("Autonomous Vernacular Copilot • Multi-Turn Voice + Proactive Insights + Fraud Shield")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio_bytes" not in st.session_state:
    st.session_state.last_audio_bytes = None

col1, col2, col3 = st.columns(3)
col1.metric("Today's QR Sales", "₹14,850", "+12% vs avg")
col2.metric("Pending Settlement", "₹4,200", "UTR: 431988271092", delta_color="off")
col3.metric("Pre-Approved Loan", "₹1.50 Lakh", "Instant Disbursal")

lang_map = {
    "Marathi (मराठी)": "mr-IN",
    "Hindi (हिंदी)": "hi-IN",
    "English (India)": "en-IN"
}
selected_lang = st.selectbox("Select Soundbox Language:", list(lang_map.keys()))
lang_code = lang_map[selected_lang]

tab1, tab2, tab3 = st.tabs(["🎙️ Voice Copilot", "☀️ Morning Briefing", "🛡️ UTR Fraud Shield"])

# TAB 1: MULTI-TURN VERNACULAR VOICE COPILOT
with tab1:
    top_bar1, top_bar2 = st.columns()
    top_bar1.write("Ask follow-up questions in Marathi, Hindi, or English:")
    if top_bar2.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    audio_value = st.audio_input("🎤 Tap mic, speak (under 25s), then tap Stop:")

    st.write("**Quick Merchant Queries (Noisy-Room Backup):**")
    q_col1, q_col2, q_col3 = st.columns(3)
    quick_query = None
    if q_col1.button("💸 Stuck ₹4,200?"):
        quick_query = "Why hasn't my ₹4,200 settlement from yesterday reached my bank yet?"
    if q_col2.button("❌ Rahul's ₹650 Failed"):
        quick_query = "Rahul's ₹650 payment failed at 10:15 AM. Was money deducted from his account?"
    if q_col3.button("🏦 Shop Loan Offer"):
        quick_query = "Am I eligible for a Paytm business loan right now and what is the daily EMI?"

    typed_query = st.chat_input("Ask a follow-up question...")
    user_query = None

    if audio_value is not None:
        audio_bytes_raw = audio_value.read()
        if audio_bytes_raw != st.session_state.last_audio_bytes:
            st.session_state.last_audio_bytes = audio_bytes_raw
            with st.spinner("Transcribing merchant voice via Saaras v3..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as raw_tmp:
                    raw_tmp.write(audio_bytes_raw)
                    raw_path = raw_tmp.name
                trimmed_path = raw_path.replace(".wav", "_trimmed.wav")
                try:
                    trim_wav_to_25s(raw_path, trimmed_path, max_seconds=25)
                    with open(trimmed_path, "rb") as f:
                        stt_resp = client.speech_to_text.transcribe(
                            file=f,
                            model="saaras:v3",
                            mode="transcribe"
                        )
                    user_query = stt_resp.transcript
                except Exception as e:
                    st.error(f"Speech-to-Text Error: {e}")
                finally:
                    for p in [raw_path, trimmed_path]:
                        if os.path.exists(p):
                            os.remove(p)
    elif quick_query:
        user_query = quick_query
    elif typed_query:
        user_query = typed_query

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Thinking with Sarvam-105B & generating Soundbox voice..."):
                try:
                    system_prompt = (
                        f"You are Paytm Sahayak in a Paytm Soundbox for Indian shopkeepers. "
                        f"Respond strictly in {selected_lang} in under 3 short sentences. "
                        f"Use ONLY this merchant data: {json.dumps(MERCHANT_DATA)}"
                    )
                    api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
                    chat_resp = client.chat.completions(
                        model="sarvam-105b",
                        max_tokens=500,
                        messages=api_messages
                    )
                    ai_reply = chat_resp.choices.message.content or "तुमचे ₹४,२०० आज दुपारी ४ वाजेपर्यंत बँकेत जमा होतील."
                    st.markdown(ai_reply)
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                    speak_text(ai_reply, lang_code)
                except Exception as e:
                    st.error(f"AI/TTS Error: {e}")

    full_convo_text = " ".join([m["content"].lower() for m in st.session_state.messages])
    if any(k in full_convo_text for k in ["4200", "4,200", "settlement", "431988271092", "अडकले", "जमा"]):
        if st.button("🎫 Auto-Raise Priority NPCI Dispute Ticket (UTR: 431988271092)"):
            st.success("✅ Ticket #PTM-99482 Raised! Priority bank escalation sent for UTR 431988271092.")
    if any(k in full_convo_text for k in ["loan", "emi", "1,50,000", "कर्ज", "लोन"]):
        if st.button("⚡ Claim Pre-Approved ₹1,50,000 Paytm Merchant Loan"):
            st.success("✅ Loan Disbursal Triggered! ₹1,50,000 will hit your bank in 10 minutes.")

# TAB 2: PROACTIVE MORNING AUDIO BRIEFING
with tab2:
    st.subheader("☀️ Proactive Smart Khata Morning Briefing")
    st.write("Paytm Soundbox proactively speaks a 15-second morning summary at shop opening.")
    if st.button("🔊 Play Today's Proactive Soundbox Briefing", type="primary"):
        with st.spinner("Generating personalized morning briefing..."):
            try:
                sys_msg = f"Write a direct 3-sentence spoken morning summary in {selected_lang} with no extra commentary."
                usr_msg = "Summarize: Yesterday sales ₹14,850 (up 12%), pending ₹4,200 settles by 4 PM today, and ₹1.50 lakh loan is pre-approved."
                resp = client.chat.completions(
                    model="sarvam-105b",
                    max_tokens=500,
                    messages=[
                        {"role": "system", "content": sys_msg},
                        {"role": "user", "content": usr_msg}
                    ]
                )
                briefing_text = resp.choices.message.content or "नमस्कार! कालची विक्री ₹१४,८५० झाली आहे. तुमचे ₹४,२०० आज दुपारी ४ वाजेपर्यंत जमा होतील आणि ₹१.५० लाखांचे कर्ज मंजूर आहे."
                st.info(briefing_text)
                speak_text(briefing_text, lang_code)
            except Exception as e:
                st.error(f"Briefing Error: {e}")

# TAB 3: FAKE PAYMENT SCREENSHOT / UTR SHIELD
with tab3:
    st.subheader("🛡️ Fake UPI Screenshot & UTR Fraud Detector")
    st.write("Verify if a customer's payment screenshot is genuine or edited using a fake UPI app.")
    uploaded_ss = st.file_uploader("Upload Customer Payment Screenshot (Optional)", type=["png", "jpg", "jpeg"])
    if uploaded_ss:
        st.image(uploaded_ss, caption="Customer Screenshot Uploaded", width=250)
    utr_input = st.text_input("Enter 12-Digit UTR / UPI Ref No.:", value="999888777666")
    if st.button("🔍 Verify UTR Against Paytm Live Ledger", type="primary"):
        verified_record = MERCHANT_DATA["recent_verified_utrs"].get(utr_input.strip())
        with st.spinner("Cross-checking Paytm Settlement Ledger..."):
            try:
                if verified_record:
                    st.success(f"✅ GENUINE PAYMENT VERIFIED! {verified_record['amount']} from {verified_record['customer']} received at {verified_record['time']}.")
                    alert_prompt = f"Say in one short reassuring sentence in {selected_lang}: Payment of {verified_record['amount']} is genuine and verified."
                else:
                    st.error(f"🚨 FRAUD ALERT — FAKE SCREENSHOT! UTR {utr_input} does NOT exist in Paytm's ledger!")
                    alert_prompt = f"Say in one short urgent warning sentence in {selected_lang}: Warning! This payment is fake and not received in your Paytm account."
                alert_resp = client.chat.completions(
                    model="sarvam-105b",
                    max_tokens=300,
                    messages=[
                        {"role": "system", "content": f"Reply in one direct spoken sentence in {selected_lang}."},
                        {"role": "user", "content": alert_prompt}
                    ]
                )
                spoken_alert = alert_resp.choices.message.content or ("हे पेमेंट खरे आहे." if verified_record else "सावधान! हा स्क्रीनशॉट बनावट आहे.")
                st.warning(spoken_alert)
                speak_text(spoken_alert, lang_code)
            except Exception as e:
                st.error(f"Verification Error: {e}")
