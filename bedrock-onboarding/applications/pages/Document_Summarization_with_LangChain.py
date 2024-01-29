import streamlit as st
import json
from io import StringIO
import uuid
import sys
import os

st.set_page_config(page_title="Amazon Bedrock Document Summary with LangChain", page_icon=":robot:", layout="wide")
st.header("Amazon Bedrock Demo- Document Summary with Langchain")


sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from helpers import *
import auth.cognito_authenticator as cognito
cognito.do_auth()

if st.session_state["enforce_login"] == 1:
    if st.session_state["auth_validated"]:
        cognito.show_button(False)
    else:
        cognito.show_button(True)
        st.write("Please login!")
        st.stop()


MAX_FILES = 1

MAP_TEMPLATE =  """
Write a concise summary of the following:
"{text}"
CONCISE SUMMARY:
"""


REDUCE_TEMPLATE = """
Write a concise summary of the following text delimited by triple backquotes.
Return your response in bullet points which covers the key points of the text.
```{text}```
BULLET POINT SUMMARY:
"""

with open('config/models.json') as llm_config:
    llm_providers = json.load(llm_config)

if "input_context" not in st.session_state:
    st.session_state.input_context = ""
    
def write_top_bar(llm_info):
    model_detail = llm_info['model_details']
    llm_code = llm_info['llm_code']

    with st.expander('Model Details'):
        st.write("#### Description")
        st.markdown(model_detail)
        st.write("#### Model Parameters")
        model_params_placeholder = st.empty()
        
        with model_params_placeholder.container():
            for p in llm_info['parameters']:
                if p['type'] == 'numeric':
                    st.slider(p['description'],min_value=p['min_value'],max_value=p['max_value'],step=p['step'],key=p['name'],value=p['default'],help=p['help'])
                else:
                    st.text_input(p['description'],key=p['name'],value=p['default'],help=p['help'])
                st.write('')
                
    with st.expander('Prompt Templates'):
        map_template = st.text_area("Map Template", key="map_template", value=MAP_TEMPLATE,height=200)
        reduce_template = st.text_area("Reduce Template", key="reduce_template", value=REDUCE_TEMPLATE,height=200)
    

def update_llm():
    if "llm_provider_selection" not in st.session_state:
        selected_llm_provider = list(llm_providers.keys())[0]
    else:
        selected_llm_provider = st.session_state.llm_provider_selection
    
    llm_info= get_llm_info(llm_providers,selected_llm_provider)
    llm_code = llm_info['llm_code']
    st.session_state['llm_code'] = llm_code
    st.session_state['llm_info'] = llm_info
    #init_model_param_values(llm_providers)
        

def handle_input(split_docs):

    llm_code = st.session_state['llm_code'] 
    llm_info = st.session_state['llm_info'] 
    map_template = st.session_state['map_template']
    reduce_template = st.session_state['reduce_template']
    output_container = st.empty() 

    with st.spinner("Getting response..."):
        result = summarize_doc(llm_info,split_docs,map_template,reduce_template)
        output_container.markdown(result)
        


st.markdown('''
This application demonstrates generating document summary using Langchain. This application uses Map-Reduce as the chain type to generate summary. This involves splitting the document into smaller batches and running summary for each of the batch(map task) and Reducing the results from the individual summaries.
'''
)
st.markdown('---')




#Initialize model param with default values
init_model_param_values(llm_providers)
update_llm()
col1, col2 = st.columns(2)
with col1:
    selected_provider = st.selectbox('Select a LLM Provider',llm_providers.keys(),key='llm_provider_selection', on_change = update_llm)
with col2:
    clear = st.button("Clear")

llm_info= get_llm_info(llm_providers,selected_provider)
write_top_bar(llm_info)

st.markdown('---')
pdf_files = st.file_uploader(f"Select a file to upload",type='pdf', accept_multiple_files=True)

if not pdf_files:
    st.info("Please upload a PDF document to continue.")
    st.stop()
else:
    if len(pdf_files) > MAX_FILES:
        st.warning(f"You have uploaded more than the limit. Remove files more than the allowed limit of {MAX_FILES} files.")
        st.stop()
    
    split_docs = pdf_to_docs(pdf_files,chunk_size=1200, chunk_overlap=100)

if clear:
    st.session_state.input = ""
    st.session_state.input_context = ""    
    

st.markdown('---')

if st.button("Summarize"):
    st.write(f'Document has {len(split_docs)} pages')
    handle_input(split_docs)

    

    
    
