# Thanawai Lertkiettikun 6740084422
# Updated : 27/11/2024 1:40PM

import streamlit as st
import openai
import json
import pandas as pd
from difflib import Differ
import re

#--------------------------------------------------------
#User Data
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "user_text" not in st.session_state:
    st.session_state.user_text = ""
if "js" not in st.session_state:
    st.session_state.js = None
if "tableChanged" not in st.session_state:
    st.session_state.tableChanged = False

#--------------------------------------------------------
#Sidebar (API Key Input)
api_key = st.sidebar.text_input(label="OpenAI API key", placeholder="Enter OpenAI API key", type="password")
st.session_state.api_key = openai.OpenAI(api_key=api_key)

#--------------------------------------------------------
#Header
st.header("PA4", divider=True)

#--------------------------------------------------------
#Text Input
st.title("English Writing Tutor")

st.text("Correct your writing, Make some quizes, and Analyze your vocabulary range.")
with st.container():
    if not st.session_state.user_text:
        user_t = st.chat_input(placeholder="Enter your writing")
        if user_t is not None and re.match(r"[A-z0-9-'\"]+", user_t):
            st.session_state.user_text = user_t
        else:
            st.warning("Input English text.")

#--------------------------------------------------------
#Ask ChatGPT for Response
if st.session_state.user_text and not st.session_state.js:
    prompt = """
My client want you to fix and teach their writing. Here is their writing:""" + " [" + st.session_state.user_text + "] " + """This is what you have to do:
1. Error correction: Identify and correct grammatical errors, spelling mistakes, and unclear phrasing in the provided text. And make an explanation input to the json format "correction" for all fixes include grammar and vocabulary fix.
2. Vocabulary enhancement: Suggest synonyms for words or phrases that could be improve. The original word will be taken from the fixed text. don't use the user wrong text one.
3. Quiz creation: Create a fill-in-the-blank quiz. Each question should have one blank with four choices. The question is based on the grammatical errors or spelling mistakes identified in the first step to help the user understand their mistake in writing. the number of question is what the mistake are. If there are no errors or fixed points, create the question based on the suggested words or phrases from the second step. The number of questions is not limited to 3 questions as the example JSON file.
4. CEFR level analysis: Classify words in the corrected text based on their CEFR level (A1, A2, B1, B2, C1, C2).
The Example of the user text and json file : "A short story are a piece of prose fiction. It can typically be read in a single sitting and focuses on a self-contained incidence or series of linked incidence, with the intent of evoking a single effect or mood. The short story are one of the oldest types of literaturer and have existed in the form of legends, mythic tales, folk tales, fairy tales, tall tales, fables, and anecdotes in various ancient communities around the world. The modern short story was developed in the early 19th century."
return as a JSON file. Format in the following JSON schema and based on the instructions above:
{
"fixed_text": "A short story is a piece of prose fiction. It can typically be read in a single sitting and focuses on a self-contained incident or series of linked incidents, with the intent of evoking a single effect or mood. The short story is one of the oldest types of literature and has existed in the form of legends, mythic tales, folk tales, fairy tales, tall tales, fables, and anecdotes in various ancient communities around the world. The modern short story was developed in the early 19th century.",

"correction": {
"incorrect_words": ["are", "incidence", "incidence", "literaturer"],
"correct_words": ["is", "incident", "incidents", "literature"],
"explanations": [
    "'are' should be 'is' to match the singular subject 'short story.'",
    "'incidence' should be 'incident' to maintain consistency in the text.",
    "'incidence' should be 'incidents' to form a plural noun in the context.",
    "'literaturer' is incorrect and should be 'literature.'"
    ]
},

"suggestion": {
    "original_words": ["focused", "incident", "linked", "literature"],
    "suggested_words": [
        ["centered", "concentrated", "directed"],
        ["occasion", "event", "occurrence"],
        ["connected", "related", "associated"],
        ["writing", "works", "written works"]
    ]
},

"quiz": {
    "questions": [
        "A short story is a piece of prose fiction. It can typically be read in a single sitting and focuses on a self-contained ___ or series of linked incidents.",
        "The modern short story was developed in the early ___ century.",
        "The short story is one of the oldest types of ___ and has existed in the form of legends, mythic tales, folk tales, fairy tales, tall tales, fables, and anecdotes in various ancient communities around the world.",
        "The modern short story was developed in the early 19th ___."
    ],
"choices": [
        ["incident", "events", "story", "plot"],
        ["20th", "16th", "19th", "21st"],
        ["stories", "narratives", "genres", "literature"],
        ["century", "decade", "age", "era"]
    ],
"correct_answers": ["incident", "19th", "literature", "century"]
},

"words_range": {
    "A1": ["is", "a", "of", "on", "and", "an", "to", "the", "it", "can"],
    "A2": ["read", "single", "and", "self-contained", "oldest"],
    "B1": ["focuses", "single", "linked", "effect", "mood"],
    "B2": ["prose", "fiction", "developed"],
    "C1": ["short", "story"],
    "C2": ["literature"]
}
}
"""
    response = st.session_state.api_key.chat.completions.create(
        model = "gpt-3.5-turbo",
        response_format={"type": "json_object"},
        messages = [
            {"role": "system", "content": "You are an English language expert."},
            {"role": "user", "content": prompt}
        ]
    )
    result = response.choices[0].message.content

    #Load ChatGPT Response json file into session state
    st.session_state.js = json.loads(result)

#--------------------------------------------------------
#Function (Error correction, Vocabulary suggestion)
def highlight_string_at_index(text, hightlight_index_list, type):
    highlight = []
    
    match type:
        case "incorrect":
            color = ":red["
        case "correct":
            color = ":green["
    
    for index, word in enumerate(text.split(" ")):
        if index in hightlight_index_list:
            highlight.append(color + word + "]")
        else:
            highlight.append(word)
    return " ".join(highlight)

def get_differ_index(original, fixed):
    diff = diff = Differ().compare(fixed.split(" "), original.split(" "))
    index = []
    adjust = 0
    for diff_index, diff in enumerate(diff):
        if diff[0] == "+":
            index.append(diff_index - adjust) #เลื่อน text_index เพราะว่า remove ออกไป
        elif diff[0] == "-" or diff[0] == "?":
            adjust += 1 #เลื่อน text_index เพราะว่า remove ออกไป
    return index

#--------------------------------------------------------
#Function (Quiz)
def submit():
    #check answer and give score
    if st.session_state.current_answer:
        if st.session_state.current_answer == answer_key[st.session_state.question_num]:
            st.session_state.score += 1
        st.session_state.already_answer[st.session_state.question_num] = 1
        st.session_state.choice_selected = 1
    else:
        st.session_state.choice_selected = 0

def previous():
    if st.session_state.question_num + 1 > 1:
        st.session_state.question_num -= 1
        st.session_state.current_answer = ""

def next():
    if st.session_state.question_num + 1 < len(question):
        st.session_state.question_num += 1
        st.session_state.current_answer = ""

def restart():
    session = {"question_num": 0, "current_answer": "", "score": 0, "already_answer": [0 for i in range(len(question))], "past_answer": ["" for i in range(len(question))], "choice_selected": 1}
    for key, value in session.items():
        st.session_state[key] = value

#--------------------------------------------------------
#CEFR Word Range Function
def removeNan():
    #find the most word list
    most_word_count = 0
    for vlist in st.session_state.js["words_range"].values():
        if len(vlist) > most_word_count:
            most_word_count = len(vlist)

    #make other list have the same empty word as the most one
    for vlist in st.session_state.js["words_range"].values():
        while len(vlist) < most_word_count:
            vlist.append("")

#--------------------------------------------------------
#Output
if st.session_state.js:
    #--------------------------------------------------------
    #Correction and Suggestion
    with st.container():
        st.subheader("Your Writing")
        st.markdown(highlight_string_at_index(text=st.session_state.user_text, hightlight_index_list=get_differ_index(st.session_state.user_text, str(st.session_state.js["fixed_text"])), type="incorrect"))

        st.subheader("Corrected wrtting")
        st.markdown(highlight_string_at_index(text=str(st.session_state.js["fixed_text"]), hightlight_index_list=get_differ_index(st.session_state.user_text, str(st.session_state.js["fixed_text"])), type="correct"))

        st.subheader("Suggested Synonym")
        st.dataframe(pd.DataFrame.from_dict(pd.DataFrame.from_dict(st.session_state.js["suggestion"])[["original_words", "suggested_words"]]), hide_index=True)
    
    #--------------------------------------------------------
    #Quiz Data
    question = st.session_state.js["quiz"]["questions"]
    choices = st.session_state.js["quiz"]["choices"]
    answer_key = st.session_state.js["quiz"]["correct_answers"]

    #create session state for quiz
    session = {"question_num": 0, "current_answer": "", "score": 0, "already_answer": [0 for i in range(len(question))], "past_answer": ["" for i in range(len(question))], "choice_selected": 1}

    for key, value in session.items():
        if key not in st.session_state:
            st.session_state.setdefault(key, value)

    #Button CSS
    st.markdown("""
    <style>
    div.stButton > button:first-child {
        display: block;
        margin: 0 auto;
    </style>
    """, unsafe_allow_html=True)

    #--------------------------------------------------------
    #Quiz
    st.subheader("Quiz")
    st.markdown(f"### Score : {st.session_state.score}/{len(question)}")
    st.markdown(f"#### {str(st.session_state.question_num + 1)}. {question[st.session_state.question_num]}")

    isAnswer = st.session_state.already_answer[st.session_state.question_num]

    #Answer Button
    if not isAnswer:
        for choice in choices[st.session_state.question_num]:
            if st.button(choice, use_container_width=True, disabled=isAnswer):
                st.session_state.current_answer = choice

    if isAnswer:
        for choice in choices[st.session_state.question_num]:
            #Correct
            if choice == answer_key[st.session_state.question_num]:
                #When user select correct answer
                if choice == st.session_state.current_answer or choice == st.session_state.past_answer[st.session_state.question_num]:
                    st.success(f"{choice} (Your Answer)")
                #When user not select correct answer
                else:
                    st.success(f"{choice}")
            #Show user answer (not correct)
            elif choice == st.session_state.current_answer or choice == st.session_state.past_answer[st.session_state.question_num]:
                st.error(f"{choice} (Your Answer)")
            #show other incorrect
            else:
                st.error(f"{choice}")
        
        if not st.session_state.past_answer[st.session_state.question_num]:
            st.session_state.past_answer[st.session_state.question_num] = st.session_state.current_answer

    #Submit
    submit_button = st.button(label="Submit", on_click=submit, disabled=isAnswer) 

    #check if player already choose the choice or not
    if not st.session_state.choice_selected:
        st.error("Please select an option before submitting.")

    #Previous and Next buttons
    col1, col2 = st.columns(2)

    with col1:
        previous_button = st.button(label="<", on_click=previous)

    with col2:
        next_button = st.button(label="\>", on_click=next)

    #Restart button
    if sum(st.session_state.already_answer) == len(question):
        st.button(label="Restart", on_click=restart)

    if not st.session_state.tableChanged:
        removeNan()
        st.session_state.tableChanged = True
    
    #--------------------------------------------------------
    #Vocab Range Data
    vocab_range = st.session_state.js["words_range"]

    #For Bar Chart
    vocabRangeCount = {}
    for key, list in vocab_range.items():
        count = 0
        for item in list:
            if item != "":
                count += 1
        vocabRangeCount[key] = [count]
            
    vocabRangeDF = pd.DataFrame(vocabRangeCount).T #transpose it for bar chart
    
    #--------------------------------------------------------
    #Vocabulary Range
    st.subheader("Word Range")
    st.bar_chart(data=vocabRangeDF)
    st.table(vocab_range)