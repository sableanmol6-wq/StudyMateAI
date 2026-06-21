import pytesseract
from PIL import Image
import os
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
import csv
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import google.generativeai as genai

physics_count = 0
math_count = 0
english_count = 0
mistakes = []

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-3.1-flash-lite")

st.title("StudyMate AI")
st.write("A low-cost AI study assistant for students who cannot afford coaching.")
st.write("Features: AI answers, mistake tracking, study planner, quizzes, flashcards, and PDF report.")
st.write("Welcome to StudyMate AI 🚀")

question = st.text_input("Ask your question:")

if question:
    ai_prompt = "Answer this student question in simple words. Give short explanation, formula if needed, and final answer: " + question

    ai_response = model.generate_content(ai_prompt)

    st.subheader("AI Answer")
    st.write(ai_response.text)

    if st.button("I got this wrong"):
        with open("mistakes.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["AI", question])

        st.success("Mistake saved!")


try:
    with open("mistakes.csv", "r") as file:
        mistakes = file.readlines()

    math_count = 0
    physics_count = 0
    english_count = 0

    for line in mistakes:

        if "Mathematics" in line:
            math_count += 1

        if "Physics" in line:
            physics_count += 1

        if "English" in line:
            english_count += 1

    st.write("Total mistakes saved:", len(mistakes))
    st.write("Physics mistakes:", physics_count)
    st.write("Math mistakes:", math_count)
    st.write("English mistakes:", english_count)

except:
    st.write("Total mistakes saved: 0")
    st.write("Physics mistakes: 0")
    st.write("Math mistakes: 0")
    st.write("English mistakes: 0")
st.header("Daily Study Plan")
study_time = st.selectbox(
    "Available Study Time",
    ["2 Hours", "4 Hours", "6 Hours"]
)
if st.button("Generate Study Plan"):     

    if math_count >= physics_count and math_count >= english_count:
        focus_subject = "Mathematics"
    elif physics_count >= math_count and physics_count >= english_count:
        focus_subject = "Physics"
    else:
        focus_subject = "English"

    st.write("Focus Area:", focus_subject)

    st.write("Today's Plan:")
    if focus_subject == "Mathematics":

        if study_time == "2 Hours":
            st.write("Physics: 30 minutes")
            st.write("Mathematics: 1 hour")
            st.write("English: 30 minutes")

        elif study_time == "4 Hours":
            st.write("Physics: 1 hour")
            st.write("Mathematics: 2 hours")
            st.write("English: 1 hour")

        else:  # 6 Hours
            st.write("Physics: 2 hours")
            st.write("Mathematics: 3 hours")
            st.write("English: 1 hour")

    elif focus_subject == "Physics":

        if study_time == "2 Hours":
            st.write("Physics: 1 hour")
            st.write("Mathematics: 30 minutes")
            st.write("English: 30 minutes")

        elif study_time == "4 Hours":
            st.write("Physics: 2 hours")
            st.write("Mathematics: 1 hour")
            st.write("English: 1 hour")

        else:  # 6 Hours
            st.write("Physics: 3 hours")
            st.write("Mathematics: 2 hours")
            st.write("English: 1 hour")

    else:
        st.write("Physics: 1 hour")
        st.write("Mathematics: 1 hour")
        st.write("English: 1 hour")
    st.write("Extra practice:", focus_subject)
    st.subheader("Recommendation")
    st.header("Mistakes Chart")

    chart_data = pd.DataFrame(
        {
            "Mistakes": [physics_count, math_count, english_count]
        },
    index=["Physics", "Mathematics", "English"]
    )    

    st.bar_chart(chart_data)

    if focus_subject == "Mathematics":
        st.write("Practice derivatives and calculus today.")

    elif focus_subject == "Physics":
        st.write("Practice force, motion and energy questions.")

    else:
        st.write("Practice grammar, nouns and verbs.")
st.header("AI Quiz Generator")

quiz_topic = st.text_input("Enter quiz topic:")

if st.button("Generate Quiz"):
    quiz_prompt = "Create 5 simple multiple choice questions for students on this topic: " + quiz_topic

    quiz_response = model.generate_content(quiz_prompt)

    st.write(quiz_response.text)
    
st.header("AI Flashcard Generator")

flashcard_topic = st.text_input("Enter flashcard topic:")

if st.button("Generate Flashcards"):
    flashcard_prompt = "Create 5 simple flashcards for students on this topic. Format as Q and A: " + flashcard_topic

    flashcard_response = model.generate_content(flashcard_prompt)

    st.write(flashcard_response.text)

st.header("Download Study Report")

if st.button("Create Study Report PDF"):
    pdf_file = "study_report.pdf"

    c = canvas.Canvas(pdf_file)
    c.drawString(100, 800, "StudyMate AI - Study Report")
    c.drawString(100, 760, "Total mistakes saved: " + str(len(mistakes)))
    c.drawString(100, 730, "Physics mistakes: " + str(physics_count))
    c.drawString(100, 700, "Math mistakes: " + str(math_count))
    c.drawString(100, 670, "English mistakes: " + str(english_count))
    c.save()

    with open(pdf_file, "rb") as file:
        st.download_button(
            label="Download PDF",
            data=file,
            file_name="study_report.pdf",
            mime="application/pdf"
        )
st.header("MEXT / KOSEN Exam Mode")

exam_subject = st.selectbox(
    "Choose Subject",
    ["Physics", "Mathematics", "English"]
)

if st.button("Generate MEXT Practice Questions"):

    prompt = f"""
    Create 5 MEXT/KOSEN-style practice questions for {exam_subject}.
    Include answers at the end.
    Keep difficulty suitable for high-school students.
    """

    response = model.generate_content(prompt)

    st.write(response.text)
st.subheader("Test Result Tracker")

score = st.number_input("Enter your score out of 5:", min_value=0, max_value=5)

if st.button("Save Test Score"):
    with open("test_scores.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([exam_subject, score])

    st.success("Score saved!")
try:
    scores_df = pd.read_csv(
        "test_scores.csv",
        names=["Subject", "Score"]
    )

    st.subheader("Score Dashboard")

    st.write("Total Tests Taken:", len(scores_df))

    st.write("Average Score:",
             round(scores_df["Score"].mean(), 2))

    st.write("Latest Score:",
             scores_df["Score"].iloc[-1])

except:
    st.write("No test scores saved yet.")
st.subheader("Score Progress")

st.line_chart(scores_df["Score"])

st.subheader("Weak Subject Analyzer")

if physics_count >= math_count and physics_count >= english_count:
    weak_subject = "Physics"
elif math_count >= physics_count and math_count >= english_count:
    weak_subject = "Mathematics"
else:
    weak_subject = "English"

st.write("Weakest Subject:", weak_subject)

if weak_subject == "Physics":
    st.write("Recommendation: Practice mechanics, waves, optics, and electricity.")
elif weak_subject == "Mathematics":
    st.write("Recommendation: Practice algebra, calculus, trigonometry, and graphs.")
else:
    st.write("Recommendation: Practice grammar, vocabulary, and reading comprehension.")



uploaded_file = st.file_uploader(
    "Upload Question Image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:

    image = Image.open(uploaded_file)

    st.image(image)

    if st.button("Solve Question"):

        with st.spinner("Solving question..."):

            prompt = """
            Solve this question step by step.
            Explain clearly.
            Show formulas used.
            Give final answer.
            """

            response = model.generate_content(
                [prompt, image]
            )

            st.subheader("Solution")
            st.write(response.text)
        
