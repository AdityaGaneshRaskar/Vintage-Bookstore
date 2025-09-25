import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from math import pi

st.set_page_config(page_title="🎤 Extempore Evaluator", layout="wide")
st.title("🎤 Extempore Speech Evaluator")

uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/mp3")

    if st.button("Analyze Speech"):
        with st.spinner("Analyzing your speech... ⏳"):
            files = {"file": uploaded_file}
            response = requests.post("http://127.0.0.1:8000/transcribe", files=files)

        if response.status_code == 200:
            result = response.json()

            st.subheader("📝 Transcription:")
            st.write(result["transcription"])

            st.subheader("📊 Gemini Feedback Dashboard:")

            feedback = result["feedback"]

            if "Error" not in feedback:
                categories = []
                scores = []
                for cat, details in feedback.items():
                    if "score" in details:
                        categories.append(cat)
                        scores.append(details["score"])

                df = pd.DataFrame({"Category": categories, "Score": scores})

                col1, col2 = st.columns([2, 1])

                # Left side = Detailed feedback
                with col1:
                    for category, details in feedback.items():
                        st.markdown(f"### 🔹 {category}")
                        st.progress(details["score"] / 10)
                        st.success(f"**Feedback:** {details['comment']}")
                        st.warning("**Improvements:**")
                        for point in details.get("improvements", []):
                            st.markdown(f"- {point}")

                # Right side = Charts
                with col2:
                    st.markdown("### 📈 Bar Chart")
                    fig, ax = plt.subplots()
                    ax.barh(df["Category"], df["Score"], color="skyblue")
                    ax.set_xlim(0, 10)
                    ax.set_xlabel("Score (out of 10)")
                    st.pyplot(fig)

                    st.markdown("### 🕸 Radar Chart")
                    N = len(categories)
                    angles = [n / float(N) * 2 * pi for n in range(N)]
                    scores += scores[:1]
                    angles += angles[:1]

                    fig, ax = plt.subplots(subplot_kw={'polar': True})
                    ax.plot(angles, scores, linewidth=2, linestyle='solid')
                    ax.fill(angles, scores, 'skyblue', alpha=0.4)
                    ax.set_xticks(angles[:-1])
                    ax.set_xticklabels(categories)
                    ax.set_yticks([2, 4, 6, 8, 10])
                    ax.set_title("Performance Radar")
                    st.pyplot(fig)

            else:
                st.error(feedback["Error"])
        else:
            st.error("❌ Error: Could not analyze speech. Check if backend is running.")
