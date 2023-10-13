# Amazon Bedrock Demo with Streamlit

Streamlit is an open-source Python framework for building quick user interface to demo AI/ML applications. There are two applications in this repo built with streamlit. 
You can find a more in-depth introduction to Streamlit from [Get started](https://docs.streamlit.io/library/get-started) page.


<img src="images/chat-with-doc.gif" alt="Streamlit application" style="width: 750px;"/>

This repo provides following applications

#### 1. Chat with a document: 
This application demonstrates how to build conversational systems with an LLM. You can select one or more PDF documents and the contents from the documents will be "stuffed" into the prompt. Text is extracted from the uploaded documents and cleaned-up. You can select what pages need to be added to the prompt. LLM gets this information as a context and you can query with your supplied context. 

#### 2. Conversational Chatbot with RAG: 
This application demonstrates Retrieval Augmented Generation (RAG) architecture. RAG can be used to retrieve data from outside a foundation model and augment your prompts by adding the relevant retrieved data in context. 

#### 3. Document Analysis: 
This application demonstrates document analysis tasks. You can select one or more documents to perform the analysis. You can use this for multiple purposes such as generating a quick summary of the or automatically generating question and answers. You can customize the prompts. This application uses Map-Reduce approach for the document analysis. This involves splitting the document into smaller batches and running the analysis task for each of the batch and collating the results from the individual groups.  

#### 4. Document summarization with Langchain: 
This application demonstrates generating document summary using Langchain. This application uses Map-Reduce as the chain type to generate summary. This involves splitting the document into smaller batches and running summary for each of the batch(map task) and Reducing the results from the individual summaries.

#### 5. RAG with Kendra: 
This application demonstrates Retrieval Augmented Generation (RAG) architecture. RAG can be used to retrieve data from outside a foundation model and augment your prompts by adding the relevant retrieved data in context. This external data used to augment prompts can come from multiple data sources, such as a document repositories, databases, or APIs. Typically documents are conveted and the application queries the data to perform relevancy search. In this case, Kendra is used as a knowledge store for the user queries. RAG model sources relevant data from the knowledge library. The original user prompt is then appended with relevant context from similar documents within the knowledge library. This augmented prompt is then sent to the foundation model. You can use Kendra to ingest the documents asynchronously. Expand Solution architecture below to learn more.


<br>
You can run the streamlit application either from locally or from SageMaker Studio


# A) Instructions to run locally
Follow the below instructions to run the application locally. 

### Install and Setup
Execute the following commands from terminal. Create a conda environment using the environment.yml file. 

``` bash
conda env create -f environment.yml
source activate bedrock-gen-ai-app
```
### Run application 
After you have installed, run the following command to launch demo application. This runs the application to run on port 8081, restrict maximum file size for upload to 10MB. Both settings can be changed.

```bash
streamlit run Amazon_Bedrock.py --server.port 8081 --server.maxUploadSize 10
```

### Launch application UI
You can navigate to the application UI using the folowing URL format. Replace the values in angle brackets. 

http://localhost:&lt;Port&gt;/


# B) Instructions to run on SageMaker Studio
Setup Streamlit environemnt. Below assumes you have extracted code to /home/sagemaker-user/bedrock_onboarding directory

```bash
cd /home/sagemaker-user/bedrock_onboarding/applications
conda env create -f environment.yml
source activate bedrock-gen-ai-app
```
### Run application 
After you have installed, run the following command to launch demo application. This runs the application to run on port 8081, restrict maximum file size for upload to 10MB. Both settings can be changed.

```bash
streamlit run Amazon_Bedrock.py --server.port 8081 --server.maxUploadSize 10
```

### Launch application UI
If you are running this app from SageMaker studio, SageMaker automatically will use a proxy to run the application. You can navigate to the application UI using the folowing URL format. Replace the values in angle brackets. Alternatively, you can execute the code cells in the notebook [app_launcher.ipynb](app_launcher.ipynb) to create the URL for you.

https://&lt;DomainName&gt;.studio.&lt;StudioRegion&gt;.sagemaker.aws/jupyter/default/proxy/&lt;Port&gt;/




# Stop & Clean-up
To stop the application, go to terminal and kill the application Ctrl +C
Deactivate conda environment created to exit out

```bash
conda deactivate 
```

You can view all conda environments by running this command
```bash
conda env list
```

Remove the environment created

```bash
conda remove --name bedrock-gen-ai-app --all
```

To verify that the environment was removed, run
```bash
conda info --envs
```