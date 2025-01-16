from typing import Any
import json
from haystack.dataclasses import ChatMessage, ChatRole
from cryptography.fernet import Fernet
import os

from agents import Agent,ChatAgent
from chat_history import get_chat_history, update_chat_history
from prompt import get_prompt, writing_style_prompt, user_data_formatter_prompt, categories
from config import agent_settings

key = os.getenv("FERNET_KEY")
fernet = Fernet(key)

## --- Chat Response Generator --- ##
def chat_response_generator(user_name:str, media_type: str, category_type: str, data: str):

  chat_history=get_chat_history(user_name,media_type,history_type)
  agent_chat_history=agent_chat_history = [ChatMessage(content= agent_settings['agent_description'][media_type], role=ChatRole.SYSTEM,name=agent_settings['agent_name'])] 
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
        return {"status": 400, "message":"User Name already exists"}
    encrypted_password=fernet.encrypt(password.encode()).decode()
    data["credentials"].append({"user_name":user_name,"password":encrypted_password})
    file.seek(0)
    json.dump(data,file,indent=2)
  return {"status":200, "message":"Success"}

def check_user(user_name:str , password:str):
  with open('credentials.json','r') as file:
    data = json.load(file)
    for user in data["credentials"]:
      if user["user_name"] == user_name:
        decrypted_password = fernet.decrypt(user["password"].encode()).decode()
        if password == decrypted_password:
          return {"status":200,"message":"Success"}
        else:
          return {"status":400, "message":"Password didn't match"}
  return {"status":404, message:"User doesn't exist"}


# print(check_user('test02','test01password'))

## Example usage chat response generator: 
# info=" Blog Information: /n Blog Title: From Newbie to Web Developer /n Blog: Starting out in web development can feel a bit like navigating a maze with no map. In my latest blog post, I share how I went from a complete newbie to building my own websites. I talk about the struggles I faced, the resources that helped me, and some tips that might make your path a bit smoother. /n Blog Link: Metta’s Tech Bytes 🚀." 
# writing_style="Preferred Writing Style: /n no emoji,more professional"
# data = info+"/n/n"+writing_style
# data = info
# response = chat_response_generator("blog", data )
# update_history("blog",data,response)
# print(response)


## Example usage response generator
# data="no emoji /n professional /n friendly /n engaging"
# print(writing_style_prompt_generator(data))

# data = {
#   "format":"Details: Main content or update.Link (Optional): URL for more details or reference.Purpose: Reason for the post (e.g., sharing insight, seeking feedback, announcement).",
#   "content":"""
#   1/ 🚀 Exciting news! I’ve completed the backend work for the Techofes Website! 🌐 Techofes, the grand cultural fest of College of Engineering, Guindy, holds a special place in my heart 🎉

#   2/ The journey began with a basic backend structure by my senior, and I took it to the next level by designing a robust database schema in PostgreSQL 🛠️

#   3/ The Techofes API, powered by Node.js, integrates seamlessly with React.js on the frontend. 🔗

#   4/ Key API features:
#   🔑 A public route to display website info
#   📱 Admin route connected to a mobile app to monitor the fest in real-time!

#   5/ I’m ecstatic to share that this API is gearing up to go live soon! 🚀 Stay tuned for more updates! 🙌

#   #Techofes #BackendDevelopment #NodeJS #ReactJS #PostgreSQL #TechMilestone #AnnaUniversity
#   """
# }
# print(user_data_formatter(data))