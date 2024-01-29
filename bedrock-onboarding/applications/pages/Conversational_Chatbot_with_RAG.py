import streamlit as st
import uuid
import sys
import os
import json


st.set_page_config(page_title="Amazon Bedrock - Conversational chatbot using RAG", page_icon=":robot:", layout="wide")
st.header("Amazon Bedrock - Conversational chatbot using RAG")


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




MAX_FILES = 2
RAG_ARCHITECTURE = "images/rag-architecture-options.png"
MAX_HISTORY_LENGTH = 5

with open('config/models.json') as llm_config:
    llm_providers = json.load(llm_config)

def build_chain(llm_info,retriever):
    llm_code = llm_info['llm_code']
    if "prompt_template" in st.session_state:
        prompt_template = st.session_state["prompt_template"]
        llm_info["prompt_template"] = prompt_template

    st.session_state["retriever"] = retriever
    st.session_state['llm_code'] = llm_code
    

    if retriever is not None:
        st.session_state['llm_chain'] = get_chain(llm_info,retriever)
    
def update_llm():
    if "llm_provider_selection" not in st.session_state:
        selected_llm_provider = list(llm_providers.keys())[0]
    else:
        selected_llm_provider = st.session_state.llm_provider_selection
    
    llm_info= get_llm_info(llm_providers,selected_llm_provider)
    
    if "retriever" in st.session_state:
        retriever = st.session_state["retriever"]
        build_chain(llm_info,retriever)
    
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
        prompt_template = st.text_area("Your Question", key="prompt_template", value=llm_info['prompt_template'], height=200)

    with st.expander('Solution Architecture'):
        st.write('')
        st.markdown(''' 
        * Improves In vehicle experience. Owners ask questions to a virtual assistant which generates response by querying LLM.
        * Search for similarity with an index store generated from user manual documents and other knowledge stores.
        * Leverage Retrieval Augmented Generation (RAG) architecture that adds context to the prompt 
        * Components: Bedrock embeddings, Bedrock LLM, FAISS as Index store, and Langchain
        ''')
        st.write('')
        st.image(RAG_ARCHITECTURE)

def handle_input(input):

    chat_history = st.session_state["chat_history"]

    llm_chain = st.session_state['llm_chain']

    with st.chat_message("user"):
        st.markdown(input)

    with st.spinner("Running.."):
        result = run_chain(llm_chain, input, chat_history)
    answer = result['answer']
        
    with st.chat_message("assistant"):
        st.markdown(answer)
    
    with st.expander("Sources"):
        for s in result['references']:
            st.write(s)

    chat_history.append((input, answer))
    
    question_with_id = {
        'question': input,
        'id': len(st.session_state.questions)
    }
    st.session_state.questions.append(question_with_id)

    document_list = []
    if 'references' in result:
        document_list = result['references']
    
    st.session_state.answers.append({
        'answer': result,
        'sources': document_list,
        'id': len(st.session_state.questions)
    })
    
    
def render_answer(chat,answer):
    with chat:
        with st.chat_message("assistant"):
            st.markdown(answer['answer'])

def render_sources(chat,sources):
    with chat:
        with st.expander("Sources"):
            for s in sources:
                st.write(s)

def write_questions(chat,md):
    with chat:
        with st.chat_message("user"):
            st.markdown(md['question'])
    

def write_response(chat,a):
    render_answer(chat,a['answer'])
    render_sources(chat,a['sources'])

# Check if the user ID is already stored in the session state
if 'user_id' in st.session_state:
    user_id = st.session_state['user_id']
else: # If the user ID is not yet stored in the session state, generate a random UUID
    user_id = str(uuid.uuid4())
    st.session_state['user_id'] = user_id


st.markdown('''
This application demonstrates Retrieval Augmented Generation (RAG) architecture. RAG can be used to retrieve data from outside a foundation model and augment your prompts by adding the relevant retrieved data in context. 

This external data used to augment prompts can come from multiple data sources, such as a document repositories, databases, or APIs. Typically documents are conveted and the application queries the data to perform relevancy search. To make the formats compatible, the underlying knowledge base and user-submitted queries are converted to numerical representations using embedding language models. Embedding is the process by which text is given numerical representation in a vector space. RAG model architectures compare the embeddings of user queries within the vector of the knowledge library. The original user prompt is then appended with relevant context from similar documents within the knowledge library. This augmented prompt is then sent to the foundation model. You can update knowledge libraries and their relevant embeddings asynchronously. Expand Solution architecture below to learn more.
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
    clear = st.button("Clear Chat")

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
    retriever = pdf_to_retriever(pdf_files)
    build_chain(llm_info,retriever)

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
    
if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = []

if "input" not in st.session_state:
    st.session_state.input = ""

if "retriever" not in st.session_state:
    st.session_state.retriever = None

if clear:
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.input = ""
    st.session_state["chat_history"] = []
    st.session_state.retriever = None    


st.markdown('---')
chat = st.container()

with st.container():
    if len(st.session_state.chat_history) >= MAX_HISTORY_LENGTH:
        st.session_state.chat_history =  st.session_state.chat_history[-MAX_HISTORY_LENGTH:]
        st.session_state.questions = st.session_state.questions[-MAX_HISTORY_LENGTH:]
        st.session_state.answers = st.session_state.answers[-MAX_HISTORY_LENGTH:]
    
    for (q, a) in zip(st.session_state.questions, st.session_state.answers):
        write_questions(chat,q)
        write_response(chat,a)

input = st.chat_input("Ask a question")
if input:
    handle_input(input)