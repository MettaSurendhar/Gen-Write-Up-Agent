import streamlit as st
from typing import List, Dict

from prompt import categories,socials
from main import writing_style_prompt_generator,chat_response_generator,chat_history_generator
from chat_history import update_chat_history,get_chat_history,add_chat_history

### INITIALIZE SESSION STATE
if 'response_state' not in st.session_state:
  st.session_state.response_state = False

if 'category_selected' not in st.session_state:
  st.session_state.category_selected = None

if 'writing_style' not in st.session_state:
  st.session_state.writing_style = ""

if 'data' not in st.session_state:
  st.session_state.data = None

if 'post_category' not in st.session_state:
  st.session_state.post_category=None

if 'social_media' not in st.session_state:
  st.session_state.social_media=None

if 'response' not in st.session_state:
  st.session_state.response=None

if 'user_name' not in st.session_state:
  st.session_state.user_name=None

if 'api_key' not in st.session_state:
  st.session_state.api_key=None

if "text_areas" not in st.session_state:
    st.session_state.text_areas = []

if "show_add_dialog" not in st.session_state:
    st.session_state.show_add_dialog = True

if "show_confirm_dialog" not in st.session_state:
    st.session_state.show_confirm_dialog = False

### FUNCTIONS
def generate_response_instance(data:str):
  st.session_state.response_state = True

def generate_clear_instance():
  st.session_state.inp1 = st.session_state.inp2 = st.session_state.inp3 = ""

def generate_done_instance(media_type:str, history_type:str,data:str,response:str):
  update_chat_history(st.session_state.user_name,media_type,history_type,data,response)
  generate_clear_instance()
  st.session_state.inp_ws = ""

def generate_cancel_instance():
  generate_clear_instance()
  st.session_state.inp_ws = ""
  st.session_state.response_state = False

def add_text_area():
  st.session_state.text_areas.append("")

def remove_text_area():
  if st.session_state.text_areas:
    st.session_state.text_areas.pop()

def open_confirm_dialog(media_type:str, history_type:str):
  history_log_list = [text for idx, text in enumerate(st.session_state.text_areas, 1)]
  st.session_state.text_areas=[]
  generated_history = chat_history_generator(media_type,history_type,history_log_list)
  st.session_state.show_add_dialog = False
  st.session_state.show_confirm_dialog = True
  confirm_history_log(generated_history)


### DIALOG
@st.dialog("View History Log",width="large")
def view_chat_history(media_type:str, history_type:str):
  chat_history = get_chat_history(st.session_state.user_name,media_type,history_type)
  for chat in chat_history:
    st.chat_message("user" if chat.role=="user" else "assistant").markdown(chat.content)


@st.dialog("Add History Log",width="large")
def add_chat_history_log(media_type: str, history_type:str):
  if st.session_state.show_add_dialog:
    left,middle,right = st.columns([3.5 ,0.5,0.5])

    left.markdown(f"**Add all the {media_type.capitalize()} - {history_category.capitalize()} content here** ",help="click the + / - to add/remove input fields")

    if middle.button("",icon=":material/add:"):
      add_text_area()
    if right.button("",icon=":material/remove:"):
      remove_text_area()

    for index, area in enumerate(st.session_state.text_areas):
      if media_type=="linkedin":
        st.session_state.text_areas[index] = st.text_area(f"Post {index + 1}",placeholder="Enter your post content ", value=area, key=f"post_{index}")
      elif media_type=="twitter":
        st.session_state.text_areas[index] = st.text_area(f"Thread {index + 1}",placeholder="Enter all the tweets of your thread", value=area, key=f"thread_{index}")

    if st.session_state.text_areas:
      for value in st.session_state.text_areas:
        if value.strip():
          st.button("Submit",type="primary",key="enabled_text_area_submit",on_click=open_confirm_dialog,args=[media_type,history_type])
        else:
          st.button("Submit",type="primary",disabled=True,key="disabled_text_area_submit")
    

@st.dialog("Confirm History Log",width="large")
def confirm_history_log(generated_history: list):
  if st.session_state.show_confirm_dialog:
    
    print(generated_history)
    for chat in generated_history:
      st.chat_message("user" if chat._role=="user" else "assistant").markdown(chat.text)

    if st.button("Done"):
      st.session_state.show_confirm_dialog = False
      st.session_state.text_areas=[]
      st.session_state.show_add_dialog=True 
      st.rerun()


## PAGE COMPONENTS
st.set_page_config(
    page_title="Write-Up Agent",
    page_icon="https://api.dicebear.com/9.x/identicon/svg?seed=Felix"
)

### HEADER COMPONENTS
st.title("Write-Up Agent")
st.subheader(f"AI-Powered Write-Up Assistant",divider="orange")

### SIDEBAR COMPONENTS
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 20em !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)

### SIDEBAR
with st.sidebar:
  
  st.header("CONFIG PANEL",divider="orange")
  st.markdown("")
  st.session_state.social_selected= st.selectbox("Pick the Social Media",
    [word.capitalize() for word in socials],help="select the type of the social media")
  st.session_state.category_selected= st.selectbox("Pick the Post Category",
    [word.capitalize() for word in list(categories.keys())],help="select the type of the post")

  st.session_state.post_category = categories[st.session_state.category_selected.lower()]

  st.session_state.writing_style = st.text_input("Writing Style Guidelines",help="eg: professional, friendly, engaging",placeholder="optional",key="inp_ws")
  
  st.markdown("---")

  
  st.markdown("**HISTORY LOGS**")
   
  media_type = st.selectbox("media",[word.capitalize() for word in socials],label_visibility="collapsed")
  history_category = st.selectbox("history",[word.capitalize() for word in list(categories.keys())],label_visibility="collapsed")
  left,right = st.columns(2,vertical_alignment ="bottom",gap="small")
  if right.button("View History",use_container_width=True):
    view_chat_history(media_type.lower(),history_category.lower())
  if left.button("Add History",use_container_width=True):
    add_chat_history_log(media_type.lower(),history_category.lower())

### CHAT 
inputs = list(st.session_state.post_category.items())

#### USER INPUT
with st.chat_message("user"):
  st.markdown(f"**{st.session_state.social_selected.upper()} - {st.session_state.category_selected.upper()} INFORMATION**")
  key1,value1 = inputs[0]
  key2,value2 = inputs[1]
  key3,value3 = inputs[2]
  inp1 = st.text_input(f"**{key1}**",placeholder=value1,key="inp1")
  inp2 = st.text_area(f"**{key2}**",placeholder=value2,key="inp2",height=150)
  inp3 = st.text_area(f"**{key3}**",placeholder=value3,key="inp3",height=68)
  st.session_state.data=f"{key1}:{inp1},/n{key2}:{inp2},/n{key3}:{inp3}"

  l1,l2,l3,middle,right = st.columns(5)
  middle.button("Clear",type="secondary",use_container_width=True,on_click=generate_clear_instance)
  
  if st.session_state.inp1.split() and st.session_state.inp2.split() and st.session_state.inp3.split():
    right.button("Generate",type="primary",use_container_width=True,on_click=generate_response_instance,args=[st.session_state.data])
  else:
    right.button("Generate",type="primary",use_container_width=True,disabled=True,on_click=generate_response_instance,args=[st.session_state.data])
  

#### DISPLAY Response
if st.session_state.response_state:
  with st.chat_message("assistant"):
    with st.spinner("Writing✏️..."):
      st.session_state.data=st.session_state.data+"/n/n"+writing_style_prompt_generator(st.session_state.writing_style) if st.session_state.writing_style.strip() else st.session_state.data
      st.session_state.response = chat_response_generator(st.session_state.social_selected.lower(),st.session_state.category_selected.lower(),st.session_state.data)
    st.markdown(st.session_state.response)

    l1,right = st.columns([5,0.9])
    st.session_state.response_state=False
    right.button("retry",icon=":material/refresh:",use_container_width=True,on_click=generate_response_instance,args=[st.session_state.data])

  left,middle,right = st.columns([0.7,3,0.7],vertical_alignment ="bottom")
  right.button("Done",icon=":material/thumb_up:",type="primary",use_container_width=True,on_click=generate_done_instance,args=[st.session_state.category_selected.lower(),st.session_state.data,st.session_state.response])

  left.button("Cancel",icon=":material/close:",type="secondary",use_container_width=True,on_click=generate_cancel_instance)
