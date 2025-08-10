import fitz  # PyMuPDF
import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

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
		page_icon=":File_folder_with_arrow:",
	)

def init_messages():
	clear_button = st.sidebar.button("Clear DB", key="clear")
	if clear_button and "vectorstore" in st.session_state:
		del st.session_state.vectorstore

def get_pdf_text():
	pdf_file = st.file_uploader(
		label="Upload PDF",
		type=["pdf"]
	)
	if pdf_file is not None:
		doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
		text = ""
		for page in doc:
			text += page.get_text()

		text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
			model_name="text-embedding-3-small",
			# Chunk sizeは重要。大きすぎると回答時にいろんな情報を参照できない。小さすぎると文脈が理解不能
			chunk_size=500,
			chunk_overlap=0,
		)

		return text_splitter.split_text(text)
	else:
		return None

def build_vectorstore(texts):
	with st.spinner("Building vectorstore..."):
		if 'vectorstore' in st.session_state:
			st.session_state.vectorstore.add_texts(texts)
		else:
			# ベクトルDBの初期化と文書の追加
			st.session_state.vectorstore = FAISS.from_texts(
				texts,
				OpenAIEmbeddings(model="text-embedding-3-small")
			)

def page_pdf_upload_and_build_vector_db():
	st.title("Upload PDF and Build Vector DB")
	pdf_text = get_pdf_text()
	if pdf_text:
		build_vectorstore(pdf_text)

def main():
	init_page()
	page_pdf_upload_and_build_vector_db()

if __name__ == "__main__":
	main()
