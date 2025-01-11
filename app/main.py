from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import streamlit as st
import yaml

def load_config(config_path="config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


def run_ollama(message):
    config = load_config()
    llm = ChatOllama(model=config["model"]["name"],
                     temperature=config["model"]["temperature"])

    system_prompt = config["system_prompt"]
    prompt = ChatPromptTemplate.from_template(
        f"{system_prompt}\n\nOriginal Text: {{message}}\n\nProvide the following structure:\n"
        f"1. Overall Evaluation: [score/5.0 and explanation]\n"
        f"2. Revision 1: [revision and evaluation]\n"
        f"3. Revision 2: [revision and evaluation]\n"
        f"4. Revision 3: [revision and evaluation]"
    )

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"message": message})

    return response

# Update the page configuration
st.set_page_config(
    page_title="Grammargeddon",
    page_icon="👽",
    layout="centered",
    initial_sidebar_state="auto"
)

def main():
    st.title("👽 Grammargeddon")

    if 'history' not in st.session_state:
        st.session_state.history = []

    user_message = st.text_input("Enter a sentence or paragraph for revision:")

    if user_message and (len(st.session_state.history) == 0 or st.session_state.history[-1][1] != user_message):
        response = run_ollama(user_message)
        st.session_state.history.append(("User", user_message))
        st.session_state.history.append(("Bot", response))
        st.session_state.user_message = ""


    st.markdown("""
        <style>
        .user-message {
            background-color: #007aff;
            color: #fafafa;
            border-radius: 15px;
            padding: 10px 15px;
            margin: 10px;
            text-align: right;
            max-width: 60%;
            float: right;
            clear: both;
            position: relative;
        }
        .user-message::after {
            content: '';
            position: absolute;
            top: 50%;
            right: -10px;
            border-width: 10px;
            border-style: solid;
            border-color: #007aff transparent transparent transparent;
            transform: translateY(-50%);
        }
        .bot-message {
            background-color: #d8d8d8;
            color: #212121;
            border-radius: 15px;
            padding: 10px 15px;
            margin: 10px;
            text-align: left;
            max-width: 90%;
            float: left;
            clear: both;
            position: relative;
        }
        .bot-message::before {
            content: '';
            position: absolute;
            top: 50%;
            left: -10px;
            border-width: 10px;
            border-style: solid;
            border-color: #e0e0e0 transparent transparent transparent;
            transform: translateY(-50%);
        }
        </style>
    """, unsafe_allow_html=True)

    if st.session_state.history:
        conversations = [(st.session_state.history[i], st.session_state.history[i + 1])
                         for i in range(0, len(st.session_state.history), 2)]

        for user_msg, bot_msg in reversed(conversations):
            if user_msg[0] == "User":
                st.markdown(
                    f"<div class='user-message'>{user_msg[1]}</div>",
                    unsafe_allow_html=True
                )
            if bot_msg[0] == "Bot":
                bot_message = f"""
                <div class='bot-message'>
                    <div style='background-color: #d8d8d8; color: #212121; border-radius: 10px; padding: 10px; margin: 5px;'>
                        <br/>
                """

                response_lines = bot_msg[1].split("\n")
                for line in response_lines:
                    if line.startswith("### "):
                        bot_message += f"<h3 style='margin: 5px 0;'>{line[4:]}</h3>"
                    elif line.startswith("- "):
                        bot_message += f"<li>{line[2:]}</li>"
                    else:
                        bot_message += f"<p>{line}</p>"

                bot_message += "</div></div>"
                st.markdown(bot_message, unsafe_allow_html=True)

if __name__ == '__main__':
    main()