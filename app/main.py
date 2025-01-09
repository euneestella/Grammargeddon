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


def main():
    st.title("👽 Grammargeddon")

    if 'history' not in st.session_state:
        st.session_state.history = []

    user_message = st.text_input("Enter a sentence or paragraph for revision:")

    if st.button("Submit"):
        if user_message:
            response = run_ollama(user_message)
            st.session_state.history.append(("User", user_message))
            st.session_state.history.append(("Bot", response))

    st.markdown("""
    <style>
    .user-message {
        background-color: #e0e0e0;
        color: #212121;
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
        text-align: right;
    }
    .bot-message {
        background-color: #fafafa;
        color: #212121;
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
        text-align: left;
    }
    .evaluation {
        font-weight: bold;
        color: #2c3e50;
    }
    .revision {
        font-style: italic;
        color: #34495e;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.history:
        for speaker, message in st.session_state.history:
            if speaker == "User":
                st.markdown(
                    f"<div class='user-message'><strong>{speaker}:</strong> {message}</div>",
                    unsafe_allow_html=True
                )
            else:
                # Parse the structured response
                response_lines = message.split("\n")
                st.markdown(f"<div class='bot-message'><strong>{speaker}:</strong></div>", unsafe_allow_html=True)
                for line in response_lines:
                    if line.startswith("Overall Evaluation"):
                        st.markdown(f"<div class='evaluation'>{line}</div>", unsafe_allow_html=True)
                    elif line.startswith("Revision"):
                        st.markdown(f"<div class='revision'>{line}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(line, unsafe_allow_html=True)

if __name__ == '__main__':
    main()