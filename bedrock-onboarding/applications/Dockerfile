# app/Dockerfile

FROM python:3.9-slim

WORKDIR /app

COPY .streamlit/ ./.streamlit/
COPY auth ./auth/
COPY config/ ./config/
COPY images/ ./images/
COPY pages/ ./pages/
COPY .env .
COPY requirements.txt .
COPY Amazon_Bedrock.py .

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:80/_stcore/health

ENTRYPOINT ["streamlit", "run", "Amazon_Bedrock.py", "--server.port=80", "--server.maxUploadSize=10"]