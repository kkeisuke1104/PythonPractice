import streamlit as st
import traceback

# load enviroment variables
from dotenv import load_dotenv
import openai
import os

import langchain_openai
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# Getting normal Website contents
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Getting Youtube Video contens (Subtitles)
from pytubefix import YouTube
import srt

# Static Propmts
SUMMARY_PROMPT = """以下のコンテンツについて300文字以内で要約してください
{content}
要約は日本語でお願いします。"""

# ------------------------Template for Flexible Chat------------------------
def init_page():
	# load environment variables
	load_dotenv()
	api_key = os.getenv("OPENAI_API_KEY")
	openai.api_key = api_key

	# set page config
	st.set_page_config(page_title="Website Summary AI", page_icon=":robot:")
	st.header("Website Summary with OpenAI")
	st.sidebar.title("Settings")

def select_model():
	# select model
	model = st.sidebar.selectbox("Select Model", ["GPT-3.5", "GPT-4"])

	#select tenmperature
	temperature = st.sidebar.slider("Temperature",min_value=0.0, max_value=1.0, value=0.5, step=0.1)

	if model == "GPT-3.5":
		st.session_state.model = "gpt-3.5-turbo"
		return ChatOpenAI(temperature=temperature, model_name="gpt-3.5-turbo")
	elif model == "GPT-4":
		st.session_state.model = "gpt-4"
		return ChatOpenAI(temperature=temperature, model_name="gpt-4")

def init_chain():
	# initialize chain
	st.session_state.llm = select_model()
	prompt = ChatPromptTemplate.from_messages([("user", SUMMARY_PROMPT)])
	output_parser = StrOutputParser()
	return prompt | st.session_state.llm | output_parser

# ------------------ Website Summary AI ------------------
def select_url_type():
	# select URL type
	url_type = st.sidebar.selectbox("Select URL Type", ["Normal Website", "YouTube Video"])

	if url_type == "Normal Website":
		st.session_state.url_type = "normal"
	elif url_type == "YouTube Video":
		st.session_state.url_type = "youtube"

	return st.session_state.url_type

def validate_url(url):
	# validate URL
	try:
		result = urlparse(url)
		return all([result.scheme, result.netloc])
	except ValueError:
		return False

def get_content_from_normal_website(url):
	try:
		with st.spinner("Fetching Website data"):
			response = requests.get(url)
			response.raise_for_status()
			soup = BeautifulSoup(response.text, 'html.parser')
			if soup.main:
				return soup.main.get_text()
			elif soup.article:
				return soup.article.get_text()
			else:
				return soup.body.get_text()
	except requests.RequestException as e:
		st.write(traceback.format_exc())
		return None

def get_content_from_youtube(url):
	try:
		# Youtubeの字幕などを取得するLoader
		yt = YouTube(url)
		captions = yt.captions

		if yt.captions:
			caption = yt.captions['a.ja']  # 'ja' for Japanese subtitles
			if not caption:
				caption = yt.captions['a.en']
			caption_srt = caption.generate_srt_captions()
			# SRTからインデックスと時刻を除去
			caption_parsed = srt.parse(caption_srt)
			# SRTの内容をテキストに変換
			caption_text = "\n".join(f"{item.content}" for item in caption_parsed)
			return caption_text
		else:
			return None
	except:
		st.write(traceback.format_exc())
		return None


def get_content(url):
	# get content from URL
	with st.spinner("Fetching Content"):
		if st.session_state.url_type == "normal":
			content = get_content_from_normal_website(url)
		elif st.session_state.url_type == "youtube":
			content = get_content_from_youtube(url)
		else:
			content = None
	return content

# -----------------Main Function-----------------

def main():
	init_page()

	# initialize chain
	chain = init_chain()
	select_url_type()

	# URLの入力チェック
	if url :=st.text_input("URL:", key=input):
		is_valid_url = validate_url(url)
		if not is_valid_url:
			st.write("Enteer valid url")
		else:
			if content := get_content(url):
				st.markdown("## Summary")
				st.write_stream(chain.stream({"content": content}))
				st.markdown("---")
				st.markdown("## Original text")
				st.write(content)

if __name__ == "__main__":
	main()
