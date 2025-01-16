import streamlit as st

# Initialize session state for input fields
if "text_areas" not in st.session_state:
    st.session_state.text_areas = []

# Function to add a new text area
def add_text_area():
    st.session_state.text_areas.append("")  # Add an empty text area

# Function to remove the last text area
def remove_text_area():
    if st.session_state.text_areas:
        st.session_state.text_areas.pop()  # Remove the last text area

st.title("Dynamic Text Areas")

# Buttons to add or remove text areas
col1, col2 = st.columns(2)
with col1:
    if st.button("➕ Add Text Area"):
        add_text_area()
with col2:
    if st.button("➖ Remove Last Text Area"):
        remove_text_area()

# Display the text areas dynamically
for idx, value in enumerate(st.session_state.text_areas):
    st.session_state.text_areas[idx] = st.text_area(f"Text Area {idx + 1}", value=value, key=f"text_area_{idx}")

# Display the final inputs
if st.button("Submit"):
    st.write("Submitted Text Areas:")
    for idx, text in enumerate(st.session_state.text_areas, 1):
        st.write(f"Text Area {idx}: {text}")
