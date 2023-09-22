import streamlit as st
import json
from io import StringIO
import uuid
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from helpers import *

MAX_FILES = 2

DFAULT_TEMPLATE = """{context}
{question}
"""

class StreamProcessor(): 
    def __init__(self, output_container):
        self.output_container = output_container
        self.combined_text = ""
    
    def streaming_handler(self, text_chunk,done=False):
        self.combined_text += text_chunk 
        self.output_container.markdown(self.combined_text + "▌")
        if done:
            self.output_container.markdown(self.combined_text)

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
                
    with st.expander('Template'):
        prompt_template = st.text_area("Prompt Template", key="prompt_template", value=DFAULT_TEMPLATE,height=200)
    
    if llm_info['streaming'] == 1:
        do_streaming = st.checkbox("Stream response", value=True, key="do_streaming", disabled=False) 
    else:
        do_streaming = st.checkbox("Stream response", value=False, key="do_streaming", disabled=True) 

def update_llm():
    if "llm_provider_selection" not in st.session_state:
        selected_llm_provider = list(llm_providers.keys())[0]
    else:
        selected_llm_provider = st.session_state.llm_provider_selection
    
    llm_info= get_llm_info(llm_providers,selected_llm_provider)
    llm_code = llm_info['llm_code']
    st.session_state['llm_code'] = llm_code
    #init_model_param_values(llm_providers)
        
def update_context(extracted_text):
    from_page = st.session_state.from_page if "from_page" in st.session_state else 1
    to_page = st.session_state.to_page if "to_page" in st.session_state else 2
    st.session_state.input_context = extracted_text[from_page-1:to_page]
    
        
def handle_input(input,do_streaming=True):

    llm_code = st.session_state['llm_code'] 
    input_context = st.session_state['input_context']
    prompt_template = st.session_state['prompt_template']
    
    executor,region,model_kwargs = get_llm_executor(llm_code)
    prompt = prompt_template.format(context=input_context,question=input)
    
    output_container = st.empty() 

    with st.spinner("Getting response..."): 
        if do_streaming:
            stream_processor = StreamProcessor(output_container)                
            executor(llm_code,prompt,region,model_kwargs,stream_processor.streaming_handler)
        else:
            result = executor(llm_code,prompt,region,model_kwargs)
            output_container.markdown(result)
        

st.set_page_config(page_title="Amazon Bedrock Conversational LLM", page_icon=":robot:", layout="wide")
st.header("Amazon Bedrock Demo- Chat with an LLM")

st.markdown('''
This application demonstrates how to build conversational systems with an LLM. You can select one or more PDF documents and the contents from the documents will be "stuffed" into the prompt. Text is extracted from the uploaded documents and cleaned-up. You can select what pages need to be added to the prompt. LLM gets this information as a context and you can query with your supplied context. 
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
pdf_files = st.file_uploader(f"Select file(s): Max {MAX_FILES} files can be uploaded",type='pdf', accept_multiple_files=True)

if not pdf_files:
    st.info("Please upload PDF documents to continue.")
    st.stop()
else:
    if len(pdf_files) > MAX_FILES:
        st.warning(f"You have uploaded more than the limit. Remove files more than the allowed limit of {MAX_FILES} files.")
        st.stop()
    
    extracted_text = pdf_to_text(pdf_files)
    total_size = len(extracted_text)
    st.write(f'Total docs uploaded: {len(pdf_files)}. There are {total_size} pages in the uploaded docs after clean-up. Select pages to add to context.')
    col1, col2   = st.columns(2)
    with col1:
        from_page = st.number_input("From Page:",key='from_page', min_value=1, max_value=total_size -1, value=1,on_change=update_context(extracted_text))
        to_page = st.number_input("To Page:", key='to_page',min_value=1, max_value=total_size -1, value=2,on_change=update_context(extracted_text))
    
    with col2:
        context_container = st.container()
        

if clear:
    st.session_state.input = ""
    st.session_state.input_context = ""    
    

st.markdown('---')

with context_container:
    st.write('')
    with st.expander('Input Context'):
        st.write('\n'.join(st.session_state.input_context))

input = st.chat_input("Ask a question")
if input:
    handle_input(input,st.session_state.do_streaming)

    
    