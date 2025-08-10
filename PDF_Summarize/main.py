import streamlit as st

# load enviroment variables
from dotenv import load_dotenv
import openai
import os

import langchain_openai
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

def init_page():
	st.set_page_config(
		page_title="ask my PDFs",
		page_icon=":books:",
	)


def main():
	# initialize the page
	init_page()

	# set page links
	st.sidebar.success("上のメニューから進んでね")

	st.markdown(
		"""
		### PDF Summarize
		- このアプリはアップロードしたPDFに対して質問できます
		- まずは左のメニューからUpload PDFを選択してPDFをアップロードしてください
		- PDFをアップロードしたら、左のメニューからAsk Questionを選択して質問を入力してください
		"""
	)

if __name__ == "__main__":
	main()
