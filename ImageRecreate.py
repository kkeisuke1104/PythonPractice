import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
import base64

# load enviroment variables
from dotenv import load_dotenv
import openai
import os

GPT4V_PROMPT = """Create a dall-e-3 prompt based on the following user input and uploaded image.

User input: {user_input}

次にアップロードされた画像に基づいてユーザーのリクエストに沿って画像を生成するためのDALL-Eプロンプトを作成してください。
プロンプトは英語で作成してください。

プロンプトではユーザーがアップロードした画像に何が描かれているか、どのようは構成になっているかを詳細に説明してください。
写真に何がうつううているかはっきりと見える場合は、示されている場所や人物の名前を正確に記述してください。
写真の構図を説明する際は、写真の中の物体や人物の位置関係を明確に記述してください。
写真の内容を可能な限り正確に再現することが重要です"""

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
	model = ChatOpenAI(model_name="gpt-4o", temperature=0.5, max_tokens=512)
	dalle3_image_url = None

	# File uploader for image
	image_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
	if image_file:
		if user_input := st.chat_input("画像をどうアレンジしたいか教えてください"):
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
							"text": GPT4V_PROMPT.format(user_input=user_input)
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

			st.markdown("### Image Prompt")
			image_prompt = st.write_stream(model.stream(query))

			with st.spinner("Generating image..."):
				# Generate image using DALL-E
				dalle3_model = DallEAPIWrapper()
				dalle3_image_url = dalle3_model.run(image_prompt)
	else:
		st.info("Please upload an image to start.")

	if dalle3_image_url:
		st.markdown("### User Input")
		st.write(user_input)
		st.image(image_file, caption="Uploaded Image", use_column_width="auto")

		st.markdown("### Generated Image")
		st.image(dalle3_image_url, caption=image_prompt, use_column_width="auto")

if __name__ == "__main__":
	main()
