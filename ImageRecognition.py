import streamlit as st
from langchain_openai import ChatOpenAI
import base64

# load enviroment variables
from dotenv import load_dotenv
import openai
import os

def init_page():
	# load environment variables
	load_dotenv()
	api_key = os.getenv("OPENAI_API_KEY")
	openai.api_key = api_key

	# set page config
	st.set_page_config(page_title="Image Recognition AI", page_icon=":robot:")
	st.header("Image Recognition with OpenAI")

def main():
	init_page()
	# Initialize OpenAI model
	model = ChatOpenAI(model_name="gpt-4o", temperature=0)

	# File uploader for image
	image_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
	if image_file:
		if user_input := st.chat_input("Ask the model about the image"):
			# Convert the image to base64 for OpenAI API
			image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
			image  = f"data:image/jpeg;base64,{image_base64}"

			# Prepare the query for the model
			query = [
				(
					"user",
					[
						{
							"type": "text",
							"text": user_input
						},
						{
							"type": "image_url",
							"image_url": {
								"url": image,
								"detail": "auto"
							}
						}
					]
				)
			]

			st.markdown("### Question")
			st.write(user_input)
			st.image(image_file)
			st.markdown("### Answer")
			st.write_stream(model.stream(query))
	else:
		st.info("Please upload an image to start.")

if __name__ == "__main__":
	main()
