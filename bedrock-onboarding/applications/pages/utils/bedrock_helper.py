import streamlit as st
import sys
import os
import json
import boto3
from botocore.config import Config

def get_llm_args(llm_code):   
    model_kwargs = {}
    if (llm_code == "anthropic.claude-v1") or (llm_code == "anthropic.claude-instant-v1") or (llm_code == "anthropic.claude-v2"):
        if st.session_state.bedrock_claude_stop_sequences == "":
            stop_sequence = []
        else:
            stop_sequence = st.session_state.bedrock_claude_stop_sequences.split(",")
        
        
        model_kwargs = {
            "max_tokens_to_sample":st.session_state.bedrock_claude_max_tokens_to_sample,
            "temperature":st.session_state.bedrock_claude_temperature,
            "top_k":st.session_state.bedrock_claude_top_k,
            "top_p":st.session_state.bedrock_claude_top_p,
            "stop_sequences": stop_sequence
            
        }
    elif (llm_code == "amazon.titan-tg1-large"):
        model_kwargs = {
            "maxTokenCount":st.session_state.bedrock_titan_max_token,
            "temperature":st.session_state.bedrock_titan_temperature,
            "topP":st.session_state.bedrock_titan_top_p,
            "stopSequences":[]
        }
    elif (llm_code == "ai21.j2-mid") or (llm_code == "ai21.j2-ultra"):
        
        if st.session_state.bedrock_ai21_stopSequences == "":
            stop_sequence = []
        else:
            stop_sequence = st.session_state.bedrock_ai21_stopSequences.split(",")
        
        model_kwargs = {
            "maxTokens":st.session_state.bedrock_ai21_maxTokens,
            "temperature":st.session_state.bedrock_ai21_temperature,
            "topP":st.session_state.bedrock_ai21_topP,
            "stopSequences":stop_sequence,
            "countPenalty":{"scale":st.session_state.bedrock_ai21_countPenalty},
            "presencePenalty":{"scale":st.session_state.bedrock_ai21_presencePenalty},
            "frequencyPenalty":{"scale":st.session_state.bedrock_ai21_frequencyPenalty},            
            
        }
        
    return model_kwargs

def get_client(region):
    session = boto3.Session()
    config = Config(retries = {
        "max_attempts":10,
        "mode":"standard"
    })

    bedrock = session.client("bedrock", region_name=region, config=config)
    return bedrock
        
    
def invoke_titan(modelId,dialog_input,region,model_kwargs,callback_handler=None):
    contentType= "application/json"
    accept= "*/*"    
    
    bedrock = get_client(region)
    payload_json = {
                    "inputText":dialog_input,
                    "textGenerationConfig":{**model_kwargs}
                   }
    
    body = json.dumps(payload_json)
    
    if callback_handler:
        response = bedrock.invoke_model_with_response_stream(
              modelId= modelId,
              contentType= contentType,
              accept= accept,
              body= body
            )
        stream = response.get('body')
        if stream:
            for event in stream:
                chunk = event.get('chunk')
                if chunk:
                    chunk_json = json.loads(chunk.get('bytes').decode())
                    callback_handler(chunk_json["outputText"]) 
            callback_handler("",True)
    else:
        response = bedrock.invoke_model(
          modelId= modelId,
          contentType= contentType,
          accept= accept,
          body= body
        )
        return json.load(response['body'])['results'][0]['outputText']

def invoke_claude(modelId,dialog_input,region,model_kwargs,callback_handler=None):
    contentType= "application/json"
    accept= "*/*"    

    bedrock = get_client(region)
    payload_json = {
                    "prompt":dialog_input,
                    **model_kwargs
                   }
    
    
    body = json.dumps(payload_json)
    
    if callback_handler:
        response = bedrock.invoke_model_with_response_stream(
              modelId= modelId,
              contentType= contentType,
              accept= accept,
              body= body
            )
        stream = response.get('body')
        if stream:
            for event in stream:
                chunk = event.get('chunk')
                if chunk:
                    chunk_json = json.loads(chunk.get('bytes').decode())
                    callback_handler(chunk_json["completion"]) 
            callback_handler("",True)
    else:
        response = bedrock.invoke_model(
          modelId= modelId,
          contentType= contentType,
          accept= accept,
          body= body
        )
        return json.load(response['body'])['completion']    
    

def invoke_ai21(modelId,dialog_input,region,model_kwargs,callback_handler=None):
    contentType= "application/json"
    accept= "*/*"    

    bedrock = get_client(region)
    payload_json = {
                    "prompt":dialog_input,
                    **model_kwargs
                   }    
    
    
    body = json.dumps(payload_json)
    # if callback_handler:
    #     response = bedrock.invoke_model_with_response_stream(
    #           modelId= modelId,
    #           contentType= contentType,
    #           accept= accept,
    #           body= body
    #         )
    #     stream = response.get('body')
    #     if stream:
    #         for event in stream:
    #             chunk = event.get('chunk')
    #             if chunk:
    #                 chunk_json = json.loads(chunk.get('bytes').decode())
    #                 callback_handler(chunk_json["completions"]['data']['text']) 
    #         callback_handler("",True)
    # else:
    response = bedrock.invoke_model(
      modelId= modelId,
      contentType= contentType,
      accept= accept,
      body= body
    )
    return json.load(response['body'])['completions'][0]['data']['text']    
    
    
def get_invoker(model):
    if model == 'amazon.titan-tg1-large':
        return invoke_titan
    elif (model == 'anthropic.claude-v1') or (model == 'anthropic.claude-instant-v1') or (model=='anthropic.claude-v2'):
        return invoke_claude
    elif (model == "ai21.j2-mid") or (model == "ai21.j2-ultra"): #(model == 'ai21.j2-grande-instruct') or (model == 'ai21.j2-jumbo-instruct'):
        return invoke_ai21
    else:
        raise Exception("Unsupported LLM: ", model)   
