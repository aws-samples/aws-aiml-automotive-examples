# Amazon Bedrock Demo with Streamlit

Streamlit is an open-source Python framework for building quick user interface to demo AI/ML applications. There are two applications in this repo built with streamlit. 
You can find a more in-depth introduction to Streamlit from [Get started](https://docs.streamlit.io/library/get-started) page.


You can run the streamlit application either from SageMaker Studio or locally.  


## Instructions to run locally
Follow the below instructions to run the application locally. 

### Install and Setup
Execute the following commands from terminal. Create a conda environment using the environment.yml file. 

``` bash
conda env create -f environment.yml
source activate bedrock-gen-ai-app
```

Run the following command after environment is created to install Amazon Bedrock client. If you haven't downloaded the client, you can download from https://d2eo22ngex1n9g.cloudfront.net/Documentation/SDK/bedrock-python-sdk.zip.

NOTE: 
This assumes that you have extracted the SDK onto /home/sagemaker-user/bedrock_onboarding/bedrock_docs/ directory. Change the path if needed. 

```bash
pip install /<extract_dir>/boto3-1.28.21-py3-none-any.whl
pip install /<extract_dir>/botocore-1.31.21-py3-none-any.whl
```


## Instructions to run on SageMaker Studio
Setup Streamlit environemnt. Below assumes you have extracted code to /home/sagemaker-user/bedrock_onboarding directory

```bash
cd /home/sagemaker-user/bedrock_onboarding/applications
conda env create -f environment.yml
source activate bedrock-gen-ai-app
```
Run the following command after environment is created to install Amazon Bedrock client. If you haven't downloaded the client, you can download from https://d2eo22ngex1n9g.cloudfront.net/Documentation/SDK/bedrock-python-sdk.zip.

NOTE: 
This assumes that you have extracted the SDK onto /home/sagemaker-user/bedrock_onboarding/bedrock_docs/ directory. Change the path if needed. 

```bash
pip install /home/sagemaker-user/bedrock_onboarding/bedrock_docs/SDK-1-28/boto3-1.28.21-py3-none-any.whl
pip install /home/sagemaker-user/bedrock_onboarding/bedrock_docs/SDK-1-28/botocore-1.31.21-py3-none-any.whl
```

## Run application 
Run the following command to launch demo application. This runs the application to run on port 8081, restrict maximum file size for upload to 10MB. Both settings can be changed.

```bash
streamlit run Amazon_Bedrock.py --server.port 8081 --server.maxUploadSize 10
```

## Stop & Clean-up
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