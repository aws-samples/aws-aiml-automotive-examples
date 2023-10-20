import streamlit as st
import uuid
import sys
import os
import json
import tempfile as tmp
import re

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.embeddings import BedrockEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.summarize import load_summarize_chain

import model_bedrock as bedrock
import bedrock_helper as bh

with open('config/settings.json') as sf:
    settings = json.load(sf)
    region = settings["region"]

def get_region():
    return region

@st.cache_resource(ttl="1h")
def _split_docs(pdf_files,chunk_size=750, chunk_overlap=150):
    docs = []
    tmpdir = tmp.TemporaryDirectory()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    
    for pdf_file in pdf_files:
        tmpfile = os.path.join(tmpdir.name, pdf_file.name)
        with open(tmpfile, "wb") as f:
            f.write(pdf_file.getvalue())
        pdfloader = PyPDFLoader(tmpfile)
        #docs.extend(pdfloader.load())
        docs.extend(pdfloader.load_and_split(text_splitter=text_splitter))

    
    #split_docs = text_splitter.split_documents(docs)
    split_docs = docs

    #Do cleanup
    for d in split_docs:
        text = d.page_content
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
        # Fix newlines in the middle of sentences
        text = re.sub(r"(?<!\n\s)\n(?!\s\n)", " ", text.strip())
        # Remove multiple newlines
        text = re.sub(r"\n\s*\n", "\n\n", text)
        #Remove hexadecimal chars
        text = re.sub(r'[/X]', "", text)
        #Remove other speciails chars
        text = re.sub(r"(\\u[0-9A-Fa-f]+)"," ",text)
        d.page_content = text
    
    return split_docs

def pdf_to_docs(pdf_files,chunk_size=750, chunk_overlap=150):
    split_docs = _split_docs(pdf_files,chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return split_docs

def pdf_to_text(pdf_files):
    split_docs = _split_docs(pdf_files)
    cleaned_text = [d.page_content for d in split_docs]
    return cleaned_text

@st.cache_resource
def pdf_to_retriever(pdf_files):
    split_docs = _split_docs(pdf_files)
    return build_retriever(region,split_docs)
   
def init_model_param_values(llm_providers):
    for d,m in llm_providers.items():
        for p in m['parameters']:
            if p['name'] not in st.session_state:
                st.session_state[p['name']] = p['default']
            
def get_llm_info(llm_providers,description):
    if description in llm_providers:
        return llm_providers[description]
    else:
        return "Uknown", "Unknown"

def get_chain(llm_info,retriever):
    llm_code = llm_info['llm_code']
    cred_profile = llm_info['credentials_profile']
    prompt_template = llm_info["prompt_template"]
    
    model_kwargs = bh.get_llm_args(llm_code)
    
    if any(model_kwargs):
        llm = bedrock.get_llm(region,cred_profile,llm_code,model_kwargs)
        return build_chain(retriever,llm,prompt_template)
        
    raise Exception("Unsupported LLM: ", llm_code)    
        
def get_llm_executor(llm_code):
    model_kwargs = bh.get_llm_args(llm_code)
    if any(model_kwargs):
        return bh.get_invoker(llm_code),region,model_kwargs 
    raise Exception("Unsupported LLM: ", llm_code)    
        
        
def build_chain(retriever,llm,prompt_template):
 
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    chain_type_kwargs = {"prompt": PROMPT}
    return RetrievalQA.from_chain_type(
        llm, 
        chain_type="stuff", 
        retriever=retriever, 
        chain_type_kwargs=chain_type_kwargs,
        return_source_documents=True
    )


def run_chain(chain, prompt: str, history=[]):
    result =  chain({"query": prompt, "chat_history": history})
    references = []
    for d in result['source_documents']:
        page = ''
        source = ''
        if 'source' in d.metadata:
            source = d.metadata['source']
        if 'page' in d.metadata:
            page = d.metadata['page']
        
        references.append({'text':d.page_content, 'source': source, 'page_no':page})
    
    return {
        "answer": result['result'],
        "references": references
    }


def build_retriever(region,split_docs):
    br = BedrockEmbeddings()
    db = FAISS.from_documents(split_docs, embedding=br)
    return db.as_retriever()

def summarize_doc(llm_info,split_docs,map_prompt,reduce_prompt):
    llm_code = llm_info['llm_code']
    cred_profile = llm_info['credentials_profile']
    prompt_template = llm_info["prompt_template"]
    
    model_kwargs = bh.get_llm_args(llm_code)
    map_template = PromptTemplate(template=map_prompt, input_variables=["text"])
    combine_template = PromptTemplate(template=reduce_prompt, input_variables=["text"])
    
    if any(model_kwargs):
        llm = bedrock.get_llm(region,cred_profile,llm_code,model_kwargs)
        summary_chain = load_summarize_chain(llm=llm,
                                    chain_type='map_reduce',
                                    map_prompt=map_template,
                                    combine_prompt=combine_template,
                                    return_intermediate_steps=False,
                                    input_key="input_documents",
                                    output_key="output_text",
                                    )
        
        output = summary_chain.run(split_docs)
        return output
        

    