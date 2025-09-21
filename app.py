# Before running this app, you need to set up your Google Cloud
# authentication. This app now supports three methods:
# 1. Setting the GOOGLE_APPLICATION_TRANSLATE_CREDENTIALS_JSON environment variable with a path to your JSON key file.
# 2. Setting the same environment variable with the raw JSON content as a single string.
# 3. Placing the JSON content of your service account key in st.secrets['GOOGLE_CREDS'].
#    This is the standard for Streamlit Cloud and can also be used locally.

import streamlit as st
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
import os
import json

def list_languages() -> dict:
    """Lists all available languages."""
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    results = translate_client.get_languages()

    for language in results:
        print("{name} ({language})".format(**language))

    return results


@st.cache_resource
def get_creds():
    """
    Loads Google Cloud credentials from an environment variable or Streamlit secrets.
    The environment variable can be either a file path or a raw JSON string.
    """
    creds_dict = None
    env_var_name = "GOOGLE_APPLICATION_TRANSLATE_CREDENTIALS_JSON"

    if env_var_name in os.environ:
        env_value = os.environ[env_var_name]
        try:
            # First, try to treat the value as a file path
            if os.path.exists(env_value) and env_value.endswith('.json'):
                with open(env_value, 'r') as f:
                    creds_dict = json.load(f)
            # If not a file path, assume it's a raw JSON string
            else:
                creds_dict = json.loads(env_value)
        except FileNotFoundError:
            st.error(f"Error: The file path specified in {env_var_name} does not exist: {env_value}")
            st.stop()
        except json.JSONDecodeError:
            st.error(f"Error decoding the JSON string or file in {env_var_name}. Please check the format.")
            st.stop()
        except Exception as e:
            st.error(f"Unexpected error loading credentials from environment variable: {e}")
            st.stop()

    # Fallback to Streamlit secrets if environment variable is not found
    elif "GOOGLE_CREDS" in st.secrets:
        try:
            creds_dict = json.loads(st.secrets["GOOGLE_CREDS"])
        except json.JSONDecodeError:
            st.error("Error decoding st.secrets['GOOGLE_CREDS']. Please check your secrets.toml format.")
        except Exception as e:
            st.error(f"Unexpected error loading st.secrets credentials: {e}")
        
    else:
        st.error("No Google credentials found. Please set GOOGLE_APPLICATION_TRANSLATE_CREDENTIALS_JSON environment variable or st.secrets['GOOGLE_CREDS'].")
        st.stop()

    return creds_dict

# Use st.cache_resource to initialize the client only once
@st.cache_resource
def get_translator_client():
    """
    Initializes and returns the Google Translate client with cached credentials.
    """
    creds = get_creds()
    if creds:
        credentials_object = service_account.Credentials.from_service_account_info(creds)
        return translate.Client(credentials=credentials_object)
    else:
        # This case is now explicitly handled in get_creds() but is a good safeguard
        return None

# Initialize the Google Translate client with the cached credentials
translate_client = get_translator_client()

# Define some common languages and their codes for the dropdown menu
LANGUAGES = {
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Chinese (Simplified)': 'zh-CN',
    'Japanese': 'ja',
    'Korean': 'ko',
    'Vietnamese': 'vi',
    'Tagalog': 'tl',
    'Russian': 'ru',
    'Hindi': 'hi',
    'Arabic': 'ar'
}

st.set_page_config(layout="centered")

st.markdown(
    """
    <style>
    .reportview-container {
        background: #f0f2f6;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    .stTextArea>div>div>textarea {
        border-radius: 10px;
    }
    .stButton>button {
        border-radius: 10px;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        padding: 10px 24px;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    </style>
    """,
    unsafe_allow_html=True
)



@st.cache_data
def translate_text(text, target_language):
    """Translates text into the target language."""
    # Add a more specific check and error message
    if not translate_client:
        st.error("Translation client could not be initialized. Please check your credentials.")
        return ""
    
    if not text:
        return ""
    
    try:
        result = translate_client.translate(text, target_language=target_language)
        return result['translatedText']
    except Exception as e:
        st.error(f"Translation failed. Error: {e}")
        return ""

def main():
    """Main function to run the Streamlit app."""
    st.title("Hage PTA  Translator :globe_with_meridians:")
    st.write("Translate school communications.")
    st.write("Traducir folletos o comunicaciones escolares.")
    st.write("Dịch tờ rơi hoặc thông tin liên lạc của trường.")
    st.write("Isalin ang mga flyer ng paaralan o komunikasyon.")

    # Text area for the user to input the original text
    original_text = st.text_area(
        "Enter the text to translate:",
        height=200,
        placeholder="e.g., 'Dear Parents, tomorrow is a half-day.'"
    )

    # Dropdown to select the target language
    target_language_name = st.selectbox(
        "Select Target Language",
        list(LANGUAGES.keys())
    )
    target_language_code = LANGUAGES[target_language_name]

    # Button to trigger the translation
    if st.button("Translate"):
        if original_text:
            with st.spinner("Translating..."):
                translated_text = translate_text(original_text, target_language_code)
                if translated_text:
                    st.subheader(f"Translated Text ({target_language_name})")
                    st.success(translated_text)
        else:
            st.warning("Please enter some text to translate.")

if __name__ == "__main__":
    main()

