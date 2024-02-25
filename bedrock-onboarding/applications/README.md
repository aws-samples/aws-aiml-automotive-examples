# Amazon Bedrock Demo with Streamlit

Streamlit is an open-source Python framework for building quick user interface to demo AI/ML applications. There are two applications in this repo built with streamlit. 
You can find a more in-depth introduction to Streamlit from [Get started](https://docs.streamlit.io/library/get-started) page.


<img src="images/chat-with-doc.gif" alt="Streamlit application" style="width: 750px;"/>

This repo provides following application functions

#### 1. Chat with a document: 
This application demonstrates how to build conversational systems with an LLM. You can select one or more PDF documents and the contents from the documents will be "stuffed" into the prompt. Text is extracted from the uploaded documents and cleaned-up. You can select what pages need to be added to the prompt. LLM gets this information as a context and you can query with your supplied context. 

#### 2. Conversational Chatbot with RAG: 
This application demonstrates Retrieval Augmented Generation (RAG) architecture. RAG can be used to retrieve data from outside a foundation model and augment your prompts by adding the relevant retrieved data in context. 

#### 3. Data Analysis with LLM:
This application demonstrates how to build an business data analytics applicaiton with LLM. You can analyze your business data with ease using our intelligent application. Simply upload your CSV files containing order data, inventory information, sales figures, or any other business metrics. The contents from the csv documents will be "stuffed" into the prompt. Text is extracted from the uploaded documents and cleaned-up. LLMs process your data from context and enable natural language conversations about your business performance.  

Ask questions about sales trends, inventory levels, customer behavior, and more to gain data-driven insights. The conversational interface allows you to have a dynamic dialogue to investigate issues, identify opportunities, and guide strategic decisions. No complex setup or long training times - just upload and analyze through intuitive questioning.

#### 4. Document Analysis: 
This application demonstrates document analysis tasks. You can select one or more documents to perform the analysis. You can use this for multiple purposes such as generating a quick summary of the or automatically generating question and answers. You can customize the prompts. This application uses Map-Reduce approach for the document analysis. This involves splitting the document into smaller batches and running the analysis task for each of the batch and collating the results from the individual groups.  

#### 5. Document summarization with Langchain: 
This application demonstrates generating document summary using Langchain. This application uses Map-Reduce as the chain type to generate summary. This involves splitting the document into smaller batches and running summary for each of the batch(map task) and Reducing the results from the individual summaries.

#### 6. RAG with Kendra: 
This application demonstrates Retrieval Augmented Generation (RAG) architecture. RAG can be used to retrieve data from outside a foundation model and augment your prompts by adding the relevant retrieved data in context. This external data used to augment prompts can come from multiple data sources, such as a document repositories, databases, or APIs. Typically documents are conveted and the application queries the data to perform relevancy search. In this case, Kendra is used as a knowledge store for the user queries. RAG model sources relevant data from the knowledge library. The original user prompt is then appended with relevant context from similar documents within the knowledge library. This augmented prompt is then sent to the foundation model. You can use Kendra to ingest the documents asynchronously. Expand Solution architecture below to learn more.

## Solution architecture
The solution architecture is based on a [pattern](https://arxiv.org/pdf/2005.11401.pdf) called Retrieval Augmented Generation (RAG) architecture. It helps to improve efficacy of large language model (LLM) based applications by using relevant enterprise domain data to synthesize a response to user queries.

<img src="images/rag-architecture-kendra.png" alt="Solution architecture" style="width: 750px;"/>

There are two parts to the solution architecture

1. Data ingestion pipeline (offline) - This ingests the domain specific documents to a Amazon Kendra index. This is done asynchronously. 
2. Runtime execution / (Online)- This handles the user queries and performs orchestration by integrating with different services.  

Following are the key services and components of this architecture.

### Key services/components

* Amazon Bedrock - a fully managed service that offers a choice of high-performing foundation models (FMs). It is serverless and users can invoke its functions via APIs to call Large Language Models (LLMs).
* Amazon Kendra - an intelligent enterprise search service, provides rich functions to perform traditional search and semantic search. It provides connectors to integrate with wide range of upstream data sources.  It is serverless and users can search the index via APIs. It supports variety of document types including .xls., doc., and .pdf
* Amazon Simple Storage Service (S3) - unstructured object storage. It provides secure, durable and scalable solution. It is serverless and documents can be uploaded through the console, API or through command line interface (CLI). Amazon Kendra can be configured to synchronize with Kendra. 
* Amazon Cognito - an identity platform for web and mobile apps. It’s a user directory, an authentication server, and an authorization service for OAuth 2.0 access tokens and AWS credentials. Application is configured with Cognito user pool for authentication. 
* Streamlit app- Front end web UI development framework written in Python.
* Amazon SageMaker Studio - Fully managed development environment for data scientists and ML engineers to run Jupyter notebooks.
* LangChain - Python based orchestration framework that helps users to develop LLM based applications. It provides support for interaction with knowledge stores like Kendra and LLMs hosted on Bedrock.
* Hosting - Application can be optionally hosted on ECS Fargate cluster. This is done by containerizing the application and docker image is stored in a ECR repository. The Streamlit application is hosted on ECS behind an Application Load Balancer. 
* Supporting services - Additional services - IAM to manage roles, and resource based permissions, CloudFormation to create resources as code, Amazon CloudWatch Metrics and Logs for observability and logging, Amazon EventBridge for event driven executions. 

### Process flow

Retrieval Augmented Generation (RAG) architecture

* User accesses a web app URL served by Streamlit based application to type their question.
* Application searches for matching document excerpts pertaining to user question. This is searched via Kendra API and it returns top matching results.
* Prompt (Input to LLM) is constructed using a template with search results, user question, and past interactions by the user. This is sent as an input for the LLM (Bedrock). This process is managed by LangChain library.
* LLM hosted by Amazon Bedrock service is invoked with the prompt via API and it generates a response.
* Response from LLM  is served to the user by the web app.

## Service access checklist
Before you proceed further, ensure following steps are carried out: 

* Ensure that you have access to Amazon Bedrock service in your account and the region you are launching these notebooks
* Review Amazon Bedrock service user guide. You can access the user guide [here.](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-service.html)
* Subscribe to the models you plan to utilize. This requires subscription to the models from AWS Marketplace for third-party models. If your account is setup with Private Marketplace, you need to subscribe to the model Ids and they need to be part of the Private Marketplace products. Refer to Bedrock User guide for details.
* Enable model access: The account does not have access to models by default. Admin users with IAM access permissions can add access to specific models using the model access page. After the admin adds access to models, those models are available for all users of the account. You will be able to see a message "Access Granted" under Model access page.
* Setup IAM policies to get access to Amazon Bedrock service. You can refer to Bedrock User Guide for a list of actions. To run this applications, add permissions to access Amazon Bedrock, S3 and Amazon Kendra services to the IAM role that is used to run the application.

## Authentication Setup with Cognito
You can optionally turn on a setting to require authentication for the application. It can authenticate against a Cognito Userpool. This application requires AppIntegration settings with Cognito user pool and you can configure to create AppIntegration and get the client secret ID. If you don't have a Cognito user pool you can create manually or using the given CloudFormation template. Follow instructions in [Cognito setup](CognitoSetup.md) to complete the setup. 

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
Setup Streamlit environment. Below assumes you have extracted code to /home/sagemaker-user/bedrock_onboarding directory

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

For SageMaker Studio classic:

https://&lt;DomainName&gt;.studio.&lt;StudioRegion&gt;.sagemaker.aws/jupyter/default/proxy/&lt;Port&gt;/

For SageMaker Studio:

https://&lt;SpaceID&gt;.studio.&lt;StudioRegion&gt;.sagemaker.aws/jupyterlab/default/proxy/&lt;Port&gt;/


# Deploy application to ECS
You can optionally deploy the Streamlit application to Amazon ECS service. Follow instructions in [Deploy to ECS](Deploy_to_ECS.md) to complete the setup. 

# Sample documents
To run the use cases, you can find sample documents in this repository. To get more details refer to this [document](sample_docs/README.md).

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