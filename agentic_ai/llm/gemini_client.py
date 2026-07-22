import google.generativeai as genai

genai.configure(api_key="YOUR_GEMINI_KEY")

model = genai.GenerativeModel("gemini-2.5-pro")