import pandas as pd
import psycopg2
import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Our Love Story & Quiz ❤️", page_icon="💖", layout="centered"
)

# --- CUSTOM CSS FOR ROMANTIC VIBE ---
st.markdown(
    """
    <style>
    .main {
        background-color: #fff0f3;
    }
    h1, h2, h3 {
        color: #d90429;
    }
    .stButton>button {
        background-color: #ff4d6d;
        color: white;
        border-radius: 20px;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #c9184a;
        color: white;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# --- DATABASE CONNECTION FUNCTION ---
def save_response_to_db(q1, q2, q3, q4, place_ans, total_score):
  try:
    db_url = st.secrets["DATABASE_URL"]
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO quiz_responses (q1_answer, q2_answer, q3_answer, q4_score, place_answered, total_score) 
        VALUES (%s, %s, %s, %s, %s, %s);
        """,
        (q1, q2, q3, q4, place_ans, total_score),
    )
    conn.commit()
    cur.close()
    conn.close()
    return True
  except Exception as e:
    return False


# --- APP HEADER ---
st.title("💖 How Well Do You Know Our Story? 💖")
st.write(
    "Welcome, my love! Take this special interactive test made just for you."
    " Answer the questions below, unlock a sweet note, and let's see your"
    " score!"
)

st.markdown("---")

# --- INITIALIZE SESSION STATE FOR QUIZ ---
if "submitted" not in st.session_state:
  st.session_state.submitted = False

# --- QUIZ FORM ---
with st.form("love_quiz_form"):
  # Question 1
  st.subheader("Question 1: What is my absolute favorite thing about you?")
  q1 = st.radio(
      "Choose the best answer:",
      [
          "Your smile and laugh",
          "Your kind heart",
          "Everything about you",
          "All of the above ❤️",
      ],
      key="q1_key",
  )

  st.markdown("---")

  # Question 2
  st.subheader("Question 2: Where was our very first official date/hangout?")
  q2 = st.text_input(
      "Type your answer here:",
      placeholder="e.g., That cozy café...",
      key="q2_key",
  )

  st.markdown("---")

  # Question 3 (Your Custom Priority Question)
  st.subheader("Question 3: Which place did you always enjoy with me the most?")
  place_options = ["Mwingi", "Mavui", "Thika", "Kimbo", "Kutus", "Kambi"]
  q_place = st.radio(
      "Choose your answer:", place_options, key="q_place_key"
  )

  st.markdown("---")

  # Question 4
  st.subheader("Question 4: Rate how much I adore you:")
  q4 = st.slider(
      "Slide to your heart's content:", 0, 100, 50, key="q4_slider_key"
  )

  submit_quiz = st.form_submit_button("Submit All Answers 💕")

# --- RESULTS & SCORING LOGIC ---
if submit_quiz:
  st.session_state.submitted = True

  score = 0

  # Q1 Scoring
  if q1 == "All of the above ❤️":
    score += 25
  else:
    score += 15

  # Q2 Scoring
  if len(q2.strip()) > 0:
    score += 25

  # Q3 Priority Scoring (Kutus > Thika > Kambi > Mwingi > Mavui > Kimbo)
  priority_scores = {
      "Kutus": 25,
      "Thika": 20,
      "Kambi": 15,
      "Mwingi": 10,
      "Mavui": 5,
      "Kimbo": 2,
  }
  score += priority_scores.get(q_place, 10)

  # Q4 Scoring
  if q4 >= 80:
    score += 25
  else:
    score += 20

  st.session_state.score = score

  # Save responses to Supabase database automatically!
  save_response_to_db(q1, q2, q_place, q4, q_place, score)

if st.session_state.submitted:
  st.markdown("---")
  st.header("🎉 Quiz Results!")

  final_score = st.session_state.score
  st.metric("Your Romantic Score", f"{final_score} / 100 pts")

  if final_score >= 75:
    st.success(
        "🏆 **Certified Soulmate Status!** You know me inside and out, and you"
        " hold the absolute key to my heart. I love you so much!"
    )
  else:
    st.success(
        "💖 **You Passed With Flying Colors!** No matter the score, you're"
        " always 100% my favorite person in the entire world."
    )

  # Romantic Note Section
  st.markdown("---")
  st.subheader("💌 A Special Note For You")
  st.info(
      "\"Thank you for bringing so much light, warmth, and joy into my life."
      " Every single memory we create together is my favorite.\"\n\n— Forever"
      " yours ❤️"
  )

# --- SECRET ADMIN VIEW FOR YOU TO CHECK HER ANSWERS ---
st.markdown("---")
with st.expander("🔒 Admin View (For Your Eyes Only)"):
  admin_pass = st.text_input("Enter your secret password:", type="password")
  if admin_pass == "Joshuangewa@1234":
    st.write("### Submitted Quiz Responses:")
    try:
      db_url = st.secrets["DATABASE_URL"]
      conn = psycopg2.connect(db_url)
      query = "SELECT created_at, q1_answer, q2_answer, place_answered, q4_score, total_score FROM quiz_responses ORDER BY created_at DESC;"
      df = pd.read_sql(query, conn)
      conn.close()
      if not df.empty:
        st.dataframe(df)
      else:
        st.info("No responses yet. Send her the link!")
    except Exception as e:
      st.error(
          "Make sure your database table columns match or DATABASE_URL is set"
          " correctly!"
      )
  elif admin_pass != "":
    st.error("Incorrect password.")
