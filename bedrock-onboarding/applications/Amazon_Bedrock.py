import streamlit as st
import json
from io import StringIO
import uuid
import sys
import os

st.set_page_config(page_title="Amazon Bedrock DemoM", page_icon=":robot:", layout="wide")
st.header("Amazon Bedrock Demo applications")

st.markdown('''

### Amazon Bedrock

Amazon Bedrock is a fully managed service that makes foundation models (FMs) from Amazon and leading AI startups available through an API, so you can choose from various FMs to find the model that's best suited for your use case. With the Amazon Bedrock serverless experience, you can quickly get started, easily experiment with FMs, privately customize FMs with your own data, and seamlessly integrate and deploy them into your applications using AWS tools and capabilities. Agents for Amazon Bedrock are fully managed and make it easier for developers to create generative-AI applications that can deliver up-to-date answers based on proprietary knowledge sources and complete tasks for a wide range of use cases.

* Choose from various FMs: You can choose FMs from Amazon, AI21 Labs, Anthropic, Cohere, and Stability AI to find the right FM for your use case. This includes the Titan, Jurassic-2, Claude, Command, and Stable Diffusion families of FMs that support different modalities including text, embeddings, and multimodal.

* Access FMs through a single API: You can use a single API to securely access customized FMs and those provided by Amazon and other AI companies. Using the same API, you can privately and more easily pass prompts and responses between the user and the FM.

* Take advantage of the fully managed experience: With the Amazon Bedrock serverless experience, you don’t need to manage the infrastructure. You can fine-tune and deploy FMs without creating instances, implementing pipelines, or setting up storage.

* Secure your generative AI applications: To secure your custom FMs, you can use AWS security services to form your in-depth security strategy. Your customized FMs are encrypted using AWS KMS keys and stored encrypted. By using AWS Identity and Access Management Service (IAM), you can control access to your customized FMs, allowing or denying access to specific FMs, as well as which services can receive inferences and who can log into the Amazon Bedrock management console.

This application launcher helps you to explore different applications built to demonstrate the features of Amazon Bedrock. 

'''
)
st.markdown('---')

st.markdown('''
### Resources:

* [Bedrock User Guide](https://d2eo22ngex1n9g.cloudfront.net/Documentation/BedrockUserGuide.pdf)
* [Bedrock API Documentation](https://docs.aws.amazon.com/bedrock/latest/APIReference/welcome.html)
* [Bedrock Python SDK](https://d2eo22ngex1n9g.cloudfront.net/Documentation/SDK/bedrock-python-sdk.zip)

''')



