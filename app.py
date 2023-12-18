import os
import streamlit as st
import base64

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

st.set_page_config(page_title="Scientific Image Analyst", layout="centered", initial_sidebar_state="collapsed")
# Streamlit page setup
st.title("Image Analyst: `GPT-4 Turbo Vision`")

# Retrieve the OpenAI API Key from secrets
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

# File uploader allows user to add their own image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Display the uploaded image
    with st.expander("Image", expanded = True):
        st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)

# Toggle for showing additional details input
show_details = st.toggle("Add details about the image", value=False)

if show_details:
    # Text input for additional details about the image, shown only if toggle is True
    additional_details = st.text_area(
        "Add any additional details or context about the image here:",
        disabled=not show_details
    )

# Button to trigger the analysis
analyze_button = st.button("Analyse Image", type="secondary")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if uploaded_file is not None and api_key and analyze_button:

    with st.spinner("Analysing the image ..."):
        # Encode the image
        base64_image = encode_image(uploaded_file)
    
        # Optimized prompt for additional clarity and detail
        prompt_text = (
            'Quero que você atue como um especialista profissional e eficiente em identificação de vitiligo e seus tipos.'
            'O vitiligo é uma doença de pele que se caracteriza pela perda da coloração da pele, chamada de hipopigmentação.'
            'Preciso de ajuda para identificar o vitiligo e seus tipos.'
            'Fornecerei a você uma imagem de um paciente com vitiligo.'
            'Você precisará me fornecer informacoes especiais do vitiligo indentificado no paciente. como por exemplo onde ele esta localizado, e o tipo'
            'Caso nao consiga identificar informacoes especiais da imagem retorne um "Nao sei"."'
        )
    
        if show_details and additional_details:
            prompt_text += (
                f"\n\nAdditional Context Provided by the User:\n{additional_details}"
            )
    
        print(prompt_text)

        # Create the payload for the completion request
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ]
    
        # Make the request to the OpenAI API
        try:
            # Stream the response
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4-vision-preview", messages=messages, 
                max_tokens=1200, stream=True
            ):
                # Check if there is content to display
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    # Warnings for user action required
    if not uploaded_file and analyze_button:
        st.warning("Please upload an image.")
    if not api_key:
        st.warning("Please enter your OpenAI API key.")
