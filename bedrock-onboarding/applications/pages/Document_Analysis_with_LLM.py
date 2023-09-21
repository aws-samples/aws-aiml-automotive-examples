import streamlit as st
import json
from io import StringIO
import uuid
import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor
from streamlit.runtime.scriptrunner import add_script_run_ctx

sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from helpers import *

MAX_FILES = 2

SUMMARIZE_CHUNK_TEMPLATE = """Summarize the following text
{text}
SUMMARY:
"""

REDUCE_TEMPLATE = """Below text has {task_type} fron multiple pages of a document. Collate the text and provide your response as markdown.
{text}
RESPONSE:
"""

QANDA_TEMPLATE = """Generate Question and Answers from the following text focusing on concepts. Return the response as markdown.
{text}
Q&A:
"""

TOPICS_TEMPLATE = """What are the topics and concepts discussed in this document? 
{text}
Response:
"""

FINDINGS_TEMPLATE = """What are the key findings from this document?.
{text}
Response:
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
                    st.slider(p['description'],min_value=p['min_value'],max_value=p['max_value'],step=p['step'],key=p['name'],value=p['default'],help=p['description'])
                else:
                    st.text_input(p['description'],key=p['name'],value=p['default'],help=p['help'])
                st.write('')
                
    with st.expander('Prompts'):
        summarize_chunk_template = st.text_area("Summarize chunks", key="summarize_chunk_template", value=SUMMARIZE_CHUNK_TEMPLATE,height=200)
        reduce_template = st.text_area("Summary of all chunks", key="reduce_template", value=REDUCE_TEMPLATE,height=200)
        qanda_template = st.text_area("Generate Q&A", key="qanda_template", value=QANDA_TEMPLATE,height=200)
        topics_template = st.text_area("Topics", key="topics_template", value=TOPICS_TEMPLATE,height=200)
        findings_template = st.text_area("Key Findings", key="findings_template", value=FINDINGS_TEMPLATE,height=200)
        
        
    
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
    st.session_state['llm_info'] = llm_info

def update_context(extracted_text):
    from_page = st.session_state.from_page if "from_page" in st.session_state else 1
    to_page = st.session_state.to_page if "to_page" in st.session_state else 2
    st.session_state.input_context = extracted_text[from_page-1:to_page]
    
def handle_summary(action_template,reduce_template,task_type,extracted_text,page_count,do_streaming=True,collate=False):

    llm_code = st.session_state['llm_code'] 
    input_context = st.session_state['input_context']
    executor,region,model_kwargs = get_llm_executor(llm_code)
    output_container = st.empty() 
    summaries = ""
    responses = {}
    batch = 1
    batch_args = []
    def submit_chunk(idx,executor,llm_code,prompt,region,model_kwargs):
        result = executor(llm_code,prompt,region,model_kwargs)
        responses[idx] = result
        output_container.markdown(f'Received response for {len(responses.keys())} of {batch}')
        
    with st.spinner("Getting response..."):
        total_pages = len(extracted_text) 
        for i in range(0,total_pages,page_count):
            context_text = extracted_text[i:i+page_count]
            prompt = action_template.format(text=context_text)
            batch_args.append({'idx':batch,'executor':executor,'llm_code':llm_code,'prompt':prompt,'region':region,'model_kwargs':model_kwargs})
            batch += 1
        
        output_container.markdown(f'Split the document into {batch} batches. Gathering {task_type}')
        with ThreadPoolExecutor(max_workers=5) as exe:
            for ba in batch_args:
                exe.submit(submit_chunk,**ba)
            for t in exe._threads:
                add_script_run_ctx(t)

        for k in sorted(responses.keys()):
            summaries += f'{task_type} #{k}:\n' + responses[k] + '\n'
        
        if collate:
            output_container.markdown('\n'.join(responses.values()))
        else:
            prompt = reduce_template.format(text=summaries,task_type=task_type)
            if do_streaming:
                stream_processor = StreamProcessor(output_container)                
                executor(llm_code,prompt,region,model_kwargs,stream_processor.streaming_handler)
            else:
                result = executor(llm_code,prompt,region,model_kwargs)
                output_container.markdown(result)

            with st.expander('Page group response'):
                st.text_area("Page group response", value=summaries,height=200, label_visibility='hidden')
            

st.set_page_config(page_title="Amazon Bedrock - Document Analysis", page_icon=":robot:", layout="wide")
st.header("Amazon Bedrock Demo- Document Analysis")
st.markdown('''
This application demonstrates document analysis tasks. You can select one or more documents to perform the analysis. You can use this for multiple purposes such as generating a quick summary of the or automatically generating question and answers. You can customize the prompts. This application uses Map-Reduce approach for the document analysis. This involves splitting the document into smaller batches and running the analysis task for each of the batch and collating the results from the individual groups.  
Following tasks are covered
* Document Summarization
* Generate Q&A
* Extract Key topics and Concepts
* Extract Key Findings
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
    st.write(f'Total docs uploaded: {len(pdf_files)}. There are {total_size} pages in the uploaded docs after clean-up. Select configuration for summarization')
    col1, col2   = st.columns(2)
    with col1:
        page_count = st.number_input("No of pages to include in a batch:",key='page_count', min_value=1, max_value=35, value=30)
    
if clear:
    st.session_state.input = ""
    st.session_state.input_context = ""    
    

st.markdown('---')

if st.button('Summarize'):
    action_template = st.session_state['summarize_chunk_template']
    reduce_template = st.session_state['reduce_template']
    handle_summary(action_template,reduce_template,"summaries",extracted_text,page_count,st.session_state.do_streaming)
    
if st.button('Generate Q&A'):
    action_template = st.session_state.qanda_template
    reduce_template = st.session_state['reduce_template']
    handle_summary(action_template,reduce_template,"question and answers",extracted_text,page_count,st.session_state.do_streaming,collate=True)
    
if st.button('Topics'):
    action_template = st.session_state.topics_template
    reduce_template = st.session_state['reduce_template']
    handle_summary(action_template,reduce_template,"topics and concepts",extracted_text,page_count,st.session_state.do_streaming)

if st.button('Key Findings'):
    action_template = st.session_state.findings_template
    reduce_template = st.session_state['reduce_template']
    handle_summary(action_template,reduce_template,"key findings",extracted_text,page_count,st.session_state.do_streaming)

    