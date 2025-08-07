import streamlit as st
import pandas as pd
from datetime import datetime
import openai
import os

openai.api_key = st.secrets["OPENAI_API_KEY"]
# Load or create CSV
csv_file = "decisions.csv"

if os.path.exists(csv_file):
    try:
        df = pd.read_csv(csv_file, encoding="utf-8")
    except UnicodeDecodeError:
        # fallback if file is in utf-16 or other encoding
        df = pd.read_csv(csv_file, encoding="utf-16")
else:
    df = pd.DataFrame(columns=["Timestamp", "Scenario", "Morale", "Stress", "Pressure", "Suggested Action"])


st.title("🧠 Leadership Decision Coach")
st.write("Describe your situation and get a suggestion powered by AI.")

# Input fields
scenario = st.text_area("Leadership scenario", placeholder="e.g., Product is behind schedule, team stressed...")
morale = st.slider("Team morale (1–10)", 1, 10, 5)
stress = st.selectbox("Stress level", ["Low", "Medium", "High"])
pressure = st.radio("Deadline pressure?", ["Yes", "No"])

# Generate suggestion using GPT
def generate_suggestion(scenario, morale, stress, pressure):
    prompt = f"""
You are an AI assistant helping leaders make thoughtful decisions.

Here’s the situation:
Scenario: {scenario}
Team morale: {morale}/10
Stress level: {stress}
Deadline pressure: {pressure}

Suggest a practical, empathetic leadership action and explain why.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        suggestion = response.choices[0].message.content.strip()
        return suggestion
    except Exception as e:
        return f"⚠️ Error getting response: {e}"

if st.button("Get AI Suggestion"):
    if scenario.strip() == "":
        st.warning("Please enter a scenario.")
    else:
        with st.spinner("Thinking..."):
            suggestion = generate_suggestion(scenario, morale, stress, pressure)
        st.success("✅ Suggestion received:")
        st.markdown(f"**💡 {suggestion}**")

        # Save to CSV
        new_row = {
            "Timestamp": datetime.now(),
            "Scenario": scenario,
            "Morale": morale,
            "Stress": stress,
            "Pressure": pressure,
            "Suggested Action": suggestion
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(csv_file, index=False)

# Show past decisions
if not df.empty:
    st.subheader("📜 Recent Decisions")
    st.dataframe(df.tail(5))
