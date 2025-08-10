import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# models
from langchain_openai import ChatOpenAI

# load enviroment variables
from dotenv import load_dotenv
import openai
import os

def init_page():
	# load environment variables
	load_dotenv()
	api_key = os.getenv("OPENAI_API_KEY")
	openai.api_key = api_key

	st.set_page_config(
		page_title="ask my PDFs",
		page_icon=":Question:",
	)

	st.sidebar.title("Options")

def select_model():
	# select model
	model = st.sidebar.selectbox("Select Model", ["GPT-3.5", "GPT-4"])

	#select tenmperature
	temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.5, step=0.1)

	if model == "GPT-3.5":
		st.session_state.model = "gpt-3.5-turbo"
		return ChatOpenAI(temperature=temperature, model_name="gpt-3.5-turbo")
	elif model == "GPT-4":
		st.session_state.model = "gpt-4"
		return ChatOpenAI(temperature=temperature, model_name="gpt-4")

def init_qa_chain():
	# initialize chain
	llm = st.session_state.llm = select_model()

	# create prompt template
	prompt = ChatPromptTemplate.from_template(
		"""
		以下の知識を用いて、ユーザーからの質問に答えてください。
		---
		前提知識
		{context}
		---
		ユーザーからの質問
		{question}
		"""
	)

	retreiver = st.session_state.vectorstore.as_retriever(
		search_type="similarity",
		#文書の取得数
		search_kwargs={"k": 10}
	)

	qa_chain = (
		{"context": retreiver, "question": RunnablePassthrough()}
		| prompt
		| llm
		| StrOutputParser()
	)
	return qa_chain

def page_ask_question():
	chain = init_qa_chain()

	if query := st.text_input("質問を入力してください"):
		st.markdown("### 回答")
		st.write_stream(chain.stream(query))

def main():
	init_page()
	st.title("PDF QA")
	if "vectorstore" not in st.session_state:
		st.warning("PDFをアップロードしてベクトルDBを構築してください。左のメニューからUpload PDFを選択してください。")
	else:
		page_ask_question()

if __name__ == "__main__":
	main()
