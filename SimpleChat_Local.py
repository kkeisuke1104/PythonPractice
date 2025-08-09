import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def main():
    # Streamlitのページ設定
    st.set_page_config(page_title="LangChain Practice", page_icon=":robot:")
    st.header("LangChain Practice with OpenAI")

    # 履歴を表示するためにst.session_stateにmessage_historyというキーに配列の会話履歴データを保存
    if "message_history" not in st.session_state:
        st.session_state.message_history = [
            ("system", "You are a helpful assistant.")
        ]

    # Set chatgpt
    llm = ChatOpenAI(base_url="http://127.0.0.1:1234/v1",
        api_key="not-needed",  # ローカルLLMではAPIキーは不要
        temperature=0.7,
        model_name="google/gemma-3-12b",  # 使用するモデル名を指定
    )
    # *はmessage_historyの配列要素を展開するために使用
    prompt = ChatPromptTemplate.from_messages([*st.session_state.message_history,
                                              ("user", "{user_input}")])
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    #
    if user_input := st.chat_input("Ask me anything:"):
        with st.spinner("Generating response..."):
            response = chain.invoke({"user_input": user_input})

        st.session_state.message_history.append(("user", user_input))
        st.session_state.message_history.append(("system", response))

        for role, message in st.session_state.get("message_history", []):
            st.chat_message(role).markdown(message)

if __name__ == "__main__":
    main()
