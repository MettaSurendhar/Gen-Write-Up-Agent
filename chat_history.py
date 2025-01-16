from haystack.dataclasses import ChatMessage, ChatRole
from typing import List
  
chat_history = {
  "Metta": {
    "linkedin": {
      "event": [],
      "blog": [],
      "experience": [],
      "contribution": [],
      "certificate": [],
      "hackathon": [],
      "project": []
    },
    "twitter": {
      "event": [],
      "blog": [],
      "experience": [],
      "contribution": [],
      "certificate": [],
      "hackathon": [],
      "project": []
    }
  }
}

def get_chat_history(user_name:str, media_type:str, history_type:str) -> List[ChatMessage]:
  return chat_history[user_name][media_type][history_type]

def update_chat_history(user_name:str, media_type:str,history_type:str, data:str, response:str):
  global chat_history
  chat_history[user_name][media_type][history_type].append(ChatMessage.from_user(data))
  chat_history[user_name][media_type][history_type].append(ChatMessage.from_assistant(response))

def add_chat_history(user_name:str, media_type:str,history_type:str, data: List[ChatMessage]):
  global chat_history
  chat_history[user_name][media_type][history_type] = chat_history[user_name][media_type][history_type] + data