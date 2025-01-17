import streamlit as st
from typing import List, Dict
from streamlit_cookies_controller import CookieController
import os
import time

from prompt import categories,socials
from main import writing_style_prompt_generator,chat_response_generator,chat_history_generator,create_user,check_user,get_registered_users
from chat_history import update_chat_history,get_chat_history,add_chat_history
from agents import set_api_key

cookie_name = os.getenv("COOKIE_NAME")
cookie_controller = CookieController(key=os.getenv("COOKIE_KEY"))

## PAGE COMPONENTS
st.set_page_config(
    page_title="Write-Up Agent",
    page_icon="https://api.dicebear.com/9.x/fun-emoji/svg?seed=Emery",
    menu_items={
      "Get help":"mailto:msurendhar8815@gmail.com",
      "Report a Bug": "https://github.com/MettaSurendhar/Gen-Write-Up-Agent/issues",
      "About": "https://github.com/MettaSurendhar/Gen-Write-Up-Agent"
    }
)

if f"{cookie_name}_logged_in" in list(cookie_controller.getAll().keys()):
  if cookie_controller.get(f"{cookie_name}_logged_in")=="True":
    st.session_state.show_authentication=False

## INITIALIZE SESSION STATE
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

if 'show_api_entry' not in st.session_state:
  st.session_state.show_api_entry=True

if "text_areas" not in st.session_state:
    st.session_state.text_areas = []

if "show_add_dialog" not in st.session_state:
    st.session_state.show_add_dialog = True

if "show_confirm_dialog" not in st.session_state:
    st.session_state.show_confirm_dialog = False

if 'show_sign_up' not in st.session_state:
  st.session_state.show_sign_up = False

if 'show_log_in' not in st.session_state:
  st.session_state.show_log_in = True

if 'show_authentication' not in st.session_state:
  st.session_state.show_authentication = True

## FUNCTIONS
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
  confirm_history_log(generated_history,media_type,history_type)


## DIALOG
@st.dialog("View History Log",width="large")
def view_chat_history(media_type:str, history_type:str):
  chat_history = get_chat_history(st.session_state.user_name,media_type,history_type)
  
  if len(chat_history) !=0:
    for chat in chat_history:
      st.chat_message("user" if chat._role=="user" else "assistant").markdown(chat.text)
  else:
    st.markdown("**_--- NO HISTORY LOGS ---_**")

  if st.button("Close"):
    st.rerun()

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
      left,middle,right = st.columns([0.6,0.6,3.5])
      for value in st.session_state.text_areas:
        if value.strip():
          left.button("Format",type="primary",key="enabled_text_area_submit",on_click=open_confirm_dialog,args=[media_type,history_type],help="formats the given data to chat history")
        else:
          left.button("Format",type="primary",disabled=True,key="disabled_text_area_submit",help="formats the given data to chat history")
      if middle.button("Cancel",type="secondary"):
        st.session_state.text_areas=[]
        st.rerun()

@st.dialog("Confirm History Log",width="large")
def confirm_history_log(generated_history: list, media_type:str, history_type:str):
  if st.session_state.show_confirm_dialog:

    for chat in generated_history:
      st.chat_message("user" if chat._role=="user" else "assistant").markdown(chat.text)

    left,middle,right = st.columns([1,0.6,3.5])
    if left.button("Add To History",type="primary",help=" Add this history of chat log to memory"):
      add_chat_history(st.session_state.user_name, media_type, history_type, generated_history)
      st.session_state.show_confirm_dialog = False
      st.session_state.show_add_dialog=True 
      st.rerun()

    if middle.button("Cancel", type="secondary"):
      st.session_state.show_confirm_dialog = False
      st.session_state.show_add_dialog=True 
      st.rerun()

if st.session_state.show_authentication:

  ## ---- AUTHENTICATION PAGE ---- ##

  ### HEADER COMPONENTS
  left,c1,c2,right = st.columns([3,1.2,8,1],vertical_alignment="center")
  c1.markdown("![logo](https://api.dicebear.com/9.x/fun-emoji/svg?seed=Emery)")
  c2.markdown("# WRITE-UP AGENT")

  st.write("")
  
  login_fragment = st.empty()
  ### SIGN UP COMPONENTS

  if st.session_state.show_sign_up:
    with st.form("sign_up",clear_on_submit=True, enter_to_submit=False):
      left,center,right = st.columns([3,1.5,2.2])
      center.markdown("### SIGN UP")
      st.write("")

      l1,m1,m2,r1 = st.columns([1.8,1.8,3,2],vertical_alignment="center")
      m1.write("**USER NAME**",help="Helps to identify user")
      user_name=m2.text_input("user_name",placeholder="Enter the user name",label_visibility="collapsed",help="User name can includes A-Z,a-z,0-9,_,- ")
      m1.write("**PASSWORD**",help="Helps to authenticate user")
      password=m2.text_input("password",placeholder="Enter the password",type="password",label_visibility="collapsed",help="Secure password must include A-Z,a-z,0-9 and other characters ")

      left,middle,right = st.columns([3,2,1])
      submitted = right.form_submit_button("**SIGN-UP**",type="primary")
      if submitted:
        if user_name.strip() and password.strip():
          with st.spinner():
            status,msg = create_user(user_name,password)
            if not status:
              st.error(msg)
            else:
              st.session_state.user_name = user_name
              cookie_controller.set(f"{cookie_name}_logged_in","True")
              st.success("Successfully Registered 🎉")
              login_fragment.balloons()
              st.session_state.show_authentication=False
              time.sleep(2)
              st.rerun()
        else:
          st.error("Please fill all the fields")

    left,c1,c2,right = st.columns([3.5,2,1,3.8],vertical_alignment="center")
    c1.write("Already Registered")
    redirect = c2.button("**Log In**",type="tertiary") 
    if redirect:
      st.session_state.show_sign_up=False
      st.session_state.show_log_in=True
      st.rerun()

  ### LOG IN COMPONENTS

  if st.session_state.show_log_in:
    with st.form("log_in",clear_on_submit=True, enter_to_submit=False):
      left,center,right = st.columns([3,1.5,2.2])
      center.markdown("### LOG IN")
      st.write("")

      l1,m1,m2,r1 = st.columns([1.8,1.8,3,2],vertical_alignment="center")
      m1.write("**USER NAME**",help="Helps to identify user")
      user_name=m2.selectbox("user_name",options=get_registered_users(),placeholder="Select the user name",label_visibility="collapsed",help="select from registered users")
      m1.write("**PASSWORD**",help="Helps to authenticate user")
      password=m2.text_input("password",placeholder="Enter the password",type="password",label_visibility="collapsed",help="Secure password must include A-Z,a-z,0-9 and other characters ")

      left,right = st.columns([5,1])
      submitted = right.form_submit_button("**LOG-IN**",type="primary")
      if submitted:
        if user_name.strip() and password.strip():
          with st.spinner():
            status,msg = check_user(user_name,password)
            if not status:
              st.error(msg)
            else:
              st.session_state.user_name = user_name
              cookie_controller.set(f"{cookie_name}_logged_in","True")
              st.success("Successfully Logged In")
              login_fragment.balloons()
              st.session_state.show_authentication=False
              time.sleep(2)
              st.rerun()
        else: 
          st.error("Please fill all the fields")

    left,c1,c2,right = st.columns([3.5,2,1,3.8],vertical_alignment="center")
    c1.write("Not Yet Registered")
    redirect = c2.button("**Sign Up**",type="tertiary") 
    if redirect:
      st.session_state.show_log_in=False
      st.session_state.show_sign_up=True
      st.rerun()


else:
  ## ---- CHAT PAGE ---- ##

  ### HEADER COMPONENTS
  left,c1,c2,right = st.columns([3,1.5,8,1],vertical_alignment="center")
  c1.markdown("![logo](https://api.dicebear.com/9.x/fun-emoji/svg?seed=Emery)")
  c2.markdown("# WRITE-UP AGENT \n #### AI-Powered Write-Up Assistant")
  left,center,right= st.columns([2,1.5,1.5])
  center.markdown(f"")

  ### SIDEBAR COMPONENTS
  st.markdown(
      """
      <style>
          section[data-testid="stSidebar"] {
              width: 22em !important; # Set the width to your desired value
          }
          div[aria-label="dialog"]> button[aria-label="Close"] {
                  display: none;}
      </style>
      """,
      unsafe_allow_html=True,
  )

  logout_fragment = st.empty()

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

    history_expander = st.expander("**HISTORY LOGS**")

    media_type = history_expander.selectbox("media",[word.capitalize() for word in socials],label_visibility="collapsed")
    history_category = history_expander.selectbox("history",[word.capitalize() for word in list(categories.keys())],label_visibility="collapsed")

    left,right = history_expander.columns(2,vertical_alignment ="bottom",gap="small")
    if right.button("View History",use_container_width=True):
      view_chat_history(media_type.lower(),history_category.lower())
    if left.button("Add History",use_container_width=True):
      add_chat_history_log(media_type.lower(),history_category.lower())

    st.markdown("---")

    if st.session_state.show_api_entry:
      st.markdown("**API Key**",help="get your api key at https://aistudio.google.com/")
      left,right = st.columns([5,1])
      st.session_state.api_key = left.text_input("",placeholder="Enter your google api key",label_visibility="collapsed",type="password")
      if right.button("",icon=":material/check:",type="primary"):
        with st.spinner("Validating"):
          valid,msg = set_api_key(st.session_state.api_key)
          if valid:
            st.success(msg)
            st.session_state.show_api_entry = False
            st.rerun()
          else:
            st.error(msg)

    else:
      if st.button("",icon=":material/key:",type="tertiary",help="Show API entry field"):
        st.session_state.show_api_entry = True
        st.session_state.api_key = None

    st.divider()
    left,center,right= st.columns([3,2,3],vertical_alignment="center")
    left.markdown(f"User : **{st.session_state.user_name}**")
    if right.button("LOG-OUT"):
      st.session_state.show_authentication=True
      st.session_state.user_name=None
      st.session_state.api_key=None
      cookie_controller.set(f"{cookie_name}_logged_in","False")
      logout_fragment.success("Successfully Logged Out")
      logout_fragment.balloons()
      time.sleep(2)
      st.rerun()
      

  ### USER INPUT
  inputs = list(st.session_state.post_category.items())
  with st.chat_message("user"):
    st.markdown(f" Enter the Information of **{st.session_state.social_selected.upper()} - {st.session_state.category_selected.upper()}**")
    key1,value1 = inputs[0]
    key2,value2 = inputs[1]
    key3,value3 = inputs[2]
    inp1 = st.text_input(f"**{key1}**",placeholder=value1,key="inp1")
    inp2 = st.text_area(f"**{key2}**",placeholder=value2,key="inp2",height=150)
    inp3 = st.text_area(f"**{key3}**",placeholder=value3,key="inp3",height=68)
    st.session_state.data=f"{key1}:{inp1},/n{key2}:{inp2},/n{key3}:{inp3}"

    l1,l2,l3,middle,right = st.columns(5)
    middle.button("Clear",type="secondary",use_container_width=True,on_click=generate_clear_instance)
    
    if st.session_state.inp1.split() and st.session_state.inp2.split() and st.session_state.inp3.split() and st.session_state.api_key.split():
      right.button("Generate",type="primary",use_container_width=True,on_click=generate_response_instance,args=[st.session_state.data])
    else:
      right.button("Generate",type="primary",use_container_width=True,disabled=True,on_click=generate_response_instance,args=[st.session_state.data])
    
  ### WARNING
  if st.session_state.show_api_entry:
    st.warning("Please enter the [api key](https://aistudio.google.com/) to generate content")

  ### DISPLAY Response
  if st.session_state.response_state:
    with st.chat_message("assistant"):
      with st.spinner("Writing✏️..."):
        st.session_state.data=st.session_state.data+"/n/n"+writing_style_prompt_generator(st.session_state.writing_style) if st.session_state.writing_style.strip() else st.session_state.data
        st.session_state.response = chat_response_generator(st.session_state.user_name,st.session_state.social_selected.lower(),st.session_state.category_selected.lower(),st.session_state.data)
      st.markdown(st.session_state.response)

      l1,right = st.columns([5,0.9])
      st.session_state.response_state=False
      right.button("retry",icon=":material/refresh:",use_container_width=True,on_click=generate_response_instance,args=[st.session_state.data])

    left,middle,right = st.columns([0.7,3,0.7],vertical_alignment ="bottom")
    right.button("Done",icon=":material/thumb_up:",type="primary",use_container_width=True,on_click=generate_done_instance,args=[st.session_state.social_selected.lower(),st.session_state.category_selected.lower(),st.session_state.data,st.session_state.response])

    left.button("Cancel",icon=":material/close:",type="secondary",use_container_width=True,on_click=generate_cancel_instance)

st.markdown("---")
left,center,right=st.columns(3,vertical_alignment="bottom")
center.markdown("Developed by **[Metta Surendhar](https://linktr.ee/MettaSurendhar)**")