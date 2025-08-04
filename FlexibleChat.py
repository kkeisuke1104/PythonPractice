import streamlit as st
import tiktoken

# load enviroment variables
from dotenv import load_dotenv
import openai
import os

import langchain_openai
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

MODEL_PRICES = {
	"input": {
		"gpt-3.5-turbo": 0.5 / 1_000_000,
		"gpt-4": 5 / 1_000_000
	},
	"output": {
		"gpt-3.5-turbo": 1.5 / 1000_000,
		"gpt-4": 15 / 1_000_000,
	}
}

def init_page():
	# load environment variables
	load_dotenv()
	api_key = os.getenv("OPENAI_API_KEY")
	openai.api_key = api_key

	# set page config
	st.set_page_config(page_title="Flexible Chat", page_icon=":robot:")
	st.header("Flexible Chat with OpenAI")
	st.sidebar.title("Settings")

def init_messages():
	# initialize message history
	clear_button = st.sidebar.button("Clear Chat History")
	if clear_button or "message_history" not in st.session_state:
		st.session_state.message_history = [
			("system", "You are a helpful assistant.")
		]

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
	prompt = ChatPromptTemplate.from_messages([*st.session_state.message_history,
											  ("user", "{user_input}")])
	output_parser = StrOutputParser()
	return prompt | st.session_state.llm | output_parser

def get_message_counts(text):
	# get message counts
	encoding = tiktoken.encoding_for_model(st.session_state.model)
	return len(encoding.encode(text))

def calculate_and_display_costs():
	input_count = 0
	output_count = 0
	for role, message in st.session_state.message_history:
		token_count = get_message_counts(message)
		if role == "user":
			input_count += token_count
		elif role == "ai":
			output_count += token_count

	# calculate costs
	if len(st.session_state.message_history) > 1:
		input_cost = MODEL_PRICES["input"][st.session_state.model] * input_count
		output_cost = MODEL_PRICES["output"][st.session_state.model] * output_count
		cost = output_cost + input_cost

	st.sidebar.markdown("### Cost Breakdown")
	st.sidebar.markdown(f"**Input Tokens:** {input_count} ({input_cost:.6f} USD)")
	st.sidebar.markdown(f"**Output Tokens:** {output_count} ({output_cost:.6f} USD)")
	st.sidebar.markdown(f"**Total Cost:** {cost:.6f} USD")

def main():
	init_page()
	init_messages()

	# initialize chain
	chain = init_chain()

	# チャット履歴の表示
	for role, message in st.session_state.get("message_history", []):
		st.chat_message(role).markdown(message)

	# Watch user input
	if user_input := st.chat_input("Ask me anything:"):
		st.chat_message("user").markdown(user_input)

		with st.chat_message('ai'):
			response = st.write_stream(chain.stream({"user_input": user_input}))

		# Add to chat history
		st.session_state.message_history.append(("user", user_input))
		st.session_state.message_history.append(("ai", response))

		# Calculate costs
		calculate_and_display_costs()

if __name__ == "__main__":
	main()
