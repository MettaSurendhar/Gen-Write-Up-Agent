from typing import Any

from agents import Agent,ChatAgent
from haystack.dataclasses import ChatMessage, ChatRole
from chat_history import get_linkedin_chat_history, get_twitter_chat_history, update_linkedin_chat_history
from prompt import get_prompt, writing_style_prompt, user_data_formatter_prompt, categories
from config import agent_settings


## --- Chat Response Generator --- ##
def chat_response_generator(media_type: str, category_type: str, data: str):

  chat_history=None
  agent_chat_history=None
  prompt=None
  if media_type == "linkedin":
    chat_history = get_linkedin_chat_history(category_type)
    agent_chat_history = [ChatMessage(content= agent_settings['agent_description'][media_type], role=ChatRole.SYSTEM,name=agent_settings['agent_name'])]
  elif media_type == "twitter":
    chat_history = get_twitter_chat_history(category_type)
    agent_chat_history = [ChatMessage(content= agent_settings['agent_description'][media_type], role=ChatRole.SYSTEM,name=agent_settings['agent_name'])]
    
  prompt = get_prompt(media_type,category_type)
  history = agent_chat_history + chat_history
  user_prompt= ChatMessage(content=prompt, role=ChatRole.USER, name="Metta")
  chat_agent = ChatAgent(history)
  result = chat_agent.run(data,user_prompt)

  response = result["response"]
  return response

# --- Response Generator --- ##

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

## Example usage chat response generator: 
# info=" Blog Information: /n Blog Title: From Newbie to Web Developer /n Blog: Starting out in web development can feel a bit like navigating a maze with no map. In my latest blog post, I share how I went from a complete newbie to building my own websites. I talk about the struggles I faced, the resources that helped me, and some tips that might make your path a bit smoother. /n Blog Link: Metta’s Tech Bytes 🚀." 
# writing_style="Preferred Writing Style: /n no emoji,more professional"
# data = info+"/n/n"+writing_style
# data = info
# response = chat_response_generator("blog", data )
# update_linkedin_chat_history("blog",data,response)
# print(response)


## Example usage response generator
# data="no emoji /n professional /n friendly /n engaging"
# print(writing_style_prompt_generator(data))

data = {
  "format":"Details: Main content or update.Link (Optional): URL for more details or reference.Purpose: Reason for the post (e.g., sharing insight, seeking feedback, announcement).",
  "content":"""
  1/ 🚀 Exciting news! I’ve completed the backend work for the Techofes Website! 🌐 Techofes, the grand cultural fest of College of Engineering, Guindy, holds a special place in my heart 🎉

  2/ The journey began with a basic backend structure by my senior, and I took it to the next level by designing a robust database schema in PostgreSQL 🛠️

  3/ The Techofes API, powered by Node.js, integrates seamlessly with React.js on the frontend. 🔗

  4/ Key API features:
  🔑 A public route to display website info
  📱 Admin route connected to a mobile app to monitor the fest in real-time!

  5/ I’m ecstatic to share that this API is gearing up to go live soon! 🚀 Stay tuned for more updates! 🙌

  #Techofes #BackendDevelopment #NodeJS #ReactJS #PostgreSQL #TechMilestone #AnnaUniversity
  """
}
print(user_data_formatter(data))