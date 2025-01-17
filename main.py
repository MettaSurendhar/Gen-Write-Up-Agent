from typing import Any
import json
from haystack.dataclasses import ChatMessage, ChatRole
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
load_dotenv()

from agents import Agent,ChatAgent
from chat_history import get_chat_history, update_chat_history,chat_history
from prompt import get_prompt, writing_style_prompt, user_data_formatter_prompt, categories
from config import agent_settings

key = os.getenv("FERNET_KEY")
fernet = Fernet(key)

## --- Chat Response Generator --- ##
def chat_response_generator(user_name:str, media_type: str, category_type: str, data: str):

  chat_history=get_chat_history(user_name,media_type,category_type)
  agent_chat_history = [ChatMessage.from_system(agent_settings['agent_description'][media_type])] 
  prompt = get_prompt(media_type,category_type)

  history = agent_chat_history + chat_history
  user_prompt= ChatMessage.from_user(prompt)
  chat_agent = ChatAgent(history)
  result = chat_agent.run(data,user_prompt)

  response = result["response"]
  return response

## --- Agent Response Generator --- ##

def writing_style_prompt_generator(data: str):
  writing_style_agent = Agent(writing_style_prompt)
  response = writing_style_agent.run(data)
  return response

def user_data_formatter(data: dict):
  data_formatter_agent = Agent(user_data_formatter_prompt)
  response = data_formatter_agent.run(data)
  return response

def chat_history_generator(media_type:str, history_type:str, data:list):
  format = categories[history_type]
  history=[]
  for datum in data:
    history.append(
      ChatMessage.from_user(
        user_data_formatter({"format":format,"content":datum})
      )
    )
    history.append(
      ChatMessage.from_assistant(datum)
    )
  
  return history


## ----- Data Handlers ---- ##

def create_user(user_name:str, password: str):
  with open('credentials.json','r+') as file:
    data = json.load(file)
    for user in data["credentials"]:
      if user["user_name"] == user_name:
        return False,"User Name already exists"
    encrypted_password=fernet.encrypt(password.encode()).decode()
    data["credentials"].append({"user_name":user_name,"password":encrypted_password})
    file.seek(0)
    json.dump(data,file,indent=2)

  chat_history.update({user_name:{
    "linkedin": {"event": [],"blog": [],"experience": [],"contribution": [],"certificate": [],"hackathon": [],"project": []},
    "twitter": {"event": [],"blog": [],"experience": [],"contribution": [],"certificate": [],"hackathon": [],"project": []}}})
  return True,"Success"

def check_user(user_name:str , password:str):
  with open('credentials.json','r') as file:
    data = json.load(file)
    for user in data["credentials"]:
      if user["user_name"] == user_name:
        decrypted_password = fernet.decrypt(user["password"].encode()).decode()
        if password == decrypted_password:
          return True,"Success"
        else:
          return False,"Password didn't match"
  return False,"User doesn't exist"

def get_registered_users():
  with open('credentials.json','r') as file:
    data = json.load(file)
    return [user["user_name"] for user in data["credentials"]]
