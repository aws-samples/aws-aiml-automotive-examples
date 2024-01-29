import streamlit as st
from dotenv import load_dotenv, dotenv_values
import requests, base64 , os
import json

load_dotenv()

if os.getenv("ENFORCE_LOGIN","") == "1":
    enforce_login = True
else:
    enforce_login = False

cognito_domain = os.getenv("COGNITO_DOMAIN","")
client_id = os.getenv("CLIENT_ID","")
client_secret = os.getenv("CLIENT_SECRET","")
callback_url = os.getenv("CALLBACK_URL","")

cognito_login_url = f"{cognito_domain}/login?client_id={client_id}&response_type=code&scope=email+openid&redirect_uri={callback_url}"
cognito_logout_url = f"{cognito_domain}/logout?client_id={client_id}&logout_uri={callback_url}"

style_sheets = """
<style>
.log {
  background-color: #008CBA;
  border: none;
  color: white !important;
  padding: 15px 32px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  margin: 4px 2px;
  cursor: pointer;
  border-radius: 12px;
}

.log:hover {
  opacity: 0.9;
  background-color: #e7e7e7; 
  color: black !important;
}

</style>
"""
def get_cognito_code():
    query_params = st.query_params
    cognito_code = ""
    if "code" in query_params:
        cognito_code = query_params["code"]
    return cognito_code


def get_tokens():
    cognito_code = get_cognito_code()
    token_url = f"{cognito_domain}/oauth2/token"
    id_secret = f"{client_id}:{client_secret}"
    id_secret_encoded = str(base64.b64encode(id_secret.encode("utf-8")), "utf-8")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {id_secret_encoded}",
    }
    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code": cognito_code,
        "redirect_uri": callback_url,
    }

    token_response = requests.post(token_url, headers=headers, data=data)
    token_response_json = token_response.json()
    access_token = ""
    id_token = ""

    if "access_token" in token_response_json:
        access_token = token_response_json["access_token"]
    
    if "id_token" in token_response_json:
        id_token = token_response_json["id_token"]    

    return access_token, id_token


def do_auth():
    if "enforce_login" not in st.session_state:
        st.session_state["enforce_login"] = 0
    if "cognito_code" not in st.session_state:
        st.session_state["cognito_code"] = ""
    if "auth_validated" not in st.session_state:
        st.session_state["auth_validated"] = False
    
    if enforce_login:
        st.session_state["enforce_login"] = 1
        access_token, id_token = get_tokens()
        if access_token != "":
            st.session_state["cognito_code"] = get_cognito_code()
            st.session_state["auth_validated"] = True
    else:
        st.session_state["enforce_login"] = 0
    

def show_button(login):
    if login:
        login_html = (style_sheets + f"<a href='{cognito_login_url}' class='log' target='_self'>Log In</a>")
        logout_html = (style_sheets + f"<a href='{cognito_logout_url}' class='log' target='_self'>Log Out</a>")
        return st.sidebar.markdown(f"{login_html}", unsafe_allow_html=True)
    else:
        logout_html = (style_sheets + f"<a href='{cognito_logout_url}' class='log' target='_self'>Log Out</a>")
        return st.sidebar.markdown(f"{logout_html}", unsafe_allow_html=True)
