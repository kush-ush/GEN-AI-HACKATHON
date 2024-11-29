import streamlit as st
import os
import time
from genai import Meeting_assist

# Initialize session state variables
if "summary_text" not in st.session_state:
    st.session_state["summary_text"] = ""
if "clarify_question" not in st.session_state:
    st.session_state["clarify_question"] = ""

st.title("Meeting Summarizer and Recorder Bot")
st.write("""
Upload a meeting link, audio, video, or PDF file, and we'll either summarize or record it for you.
If you have doubts even after reviewing the summary, use the text box for clarification.
""")

# Header for upload section
st.header("Upload Your Meeting Details")

# Input type selection
input_type = st.radio(
    "Select Input Type:",
    ("Meeting Link", "Audio File", "Video File", "PDF File")
)

# Initialize variables
user_input = None
save_path = None

# Input handling based on selected type
if input_type == "Meeting Link":
    user_input = st.text_input("Enter the Google Meet link:")
elif input_type in ["Audio File", "Video File", "PDF File"]:
    file_type = {
        "Audio File": ["mp3", "wav", "m4a"],
        "Video File": ["mp4", "mkv", "avi"],
        "PDF File": ["pdf"]
    }
    user_input = st.file_uploader(f"Upload a {input_type.lower()}:", type=file_type[input_type])

# Helper function to save files
def save_file(file, directory, filename):
    if not os.path.exists(directory):
        os.makedirs(directory)  # Create the directory if it doesn't exist
    save_path = os.path.join(directory, filename)
    with open(save_path, "wb") as f:
        f.write(file.read())
    return save_path

# Submit button
if st.button("Submit"):
    if user_input:
        if input_type == "Meeting Link":
            st.info("The bot is now joining the meeting and recording it. Please wait...")
            try:
                # Example: Call your meeting bot function here
                # from meeting_bot import join_and_record_meeting
                # join_and_record_meeting(user_input)

                st.success("The meeting has been successfully recorded!")
                st.write("Your recording will be available shortly.")
            except Exception as e:
                st.error(f"An error occurred while recording the meeting: {str(e)}")
        else:
            # Determine save directory based on file type
            if input_type == "PDF File":
                directory = "./Documents"
            elif input_type == "Audio File":
                directory = "./Audio"
            elif input_type == "Video File":
                directory = "./Video"
            else:
                directory = None
            
            if directory:
                save_path = save_file(user_input, directory, user_input.name)
                st.success("Your file has been successfully uploaded.")
                time.sleep(3)
                
                # Summarization logic
                bot = Meeting_assist()
                bot.initialize()
                st.session_state["summary_text"] = bot.summerise()  # Store summary in session state
                
                # Display the summary
                st.header("Meeting Summary")
                st.write(st.session_state["summary_text"])
    else:
        st.error("Please provide an input (link or file).")

# Display the summary if it exists in session state
if st.session_state["summary_text"]:
    st.header("Meeting Summary")
    st.write(st.session_state["summary_text"])
    
    # Clarification section
    st.session_state["clarify_question"] = st.text_area(
        "Have any doubts? Ask here for clarification:",
        value=st.session_state["clarify_question"],  # Preserve user input
        key="clarification_box"
    )
    
    if st.button("Clarify"):
        if st.session_state["clarify_question"].strip():
            with st.spinner("Processing your query..."):
                bot = Meeting_assist()
                bot.initialize()
                answer = bot.answer_from_documents(st.session_state["clarify_question"])
            st.header("Answer")
            st.write(answer)
        else:
            st.error("Please enter a question for clarification.")

# Footer
st.write("---")
st.write("Thank you for using the Meeting Summarizer and Recorder Bot!")

