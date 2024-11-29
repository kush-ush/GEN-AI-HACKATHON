import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import subprocess
import time


def join_and_record_meeting(meet_link, email, password, output_audio_file=r"D:\GenAI\meeting_audio.mp3"):
    """
    Joins a Google Meet and records the audio until the meeting ends.

    Args:
        meet_link (str): The Google Meet link.
        email (str): Google account email for the bot.
        password (str): Password for the bot's Google account.
        output_audio_file (str): Path to save the recorded audio as an MP3 file.
    """
    # Configure Selenium WebDriver with options
    chrome_options = Options()
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--mute-audio")  # Mute browser audio (record system audio instead)
    chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration

    # Replace the path with your ChromeDriver location
    service = Service(r"D:\GenAI\chromedriver-win64\chromedriver-win64\chromedriver.exe")  # Example: "C:/drivers/chromedriver.exe"
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Initialize FFmpeg process to None
    ffmpeg_process = None

    try:
        # Start FFmpeg to record system audio
        print("Starting audio recording...")
        ffmpeg_command = [
            r"D:\GenAI\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe",
            "-f", "dshow",               # For Windows; replace with `pulse` for Linux or `avfoundation` for macOS
            "-i", "audio=Microphone Array(Realtek Audio)",   # Replace 'Stereo Mix' with the correct audio device name
            "-ac", "2",                 # Number of audio channels
            "-ar", "44100",             # Audio sampling rate
            "-q:a", "3",                # Audio quality
            output_audio_file           # Output file
        ]
        ffmpeg_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Log in to Google Account
        driver.get("https://accounts.google.com/signin")
        time.sleep(3)

        # Enter email
        email_input = driver.find_element(By.ID, "identifierId")
        email_input.send_keys(email)
        email_input.send_keys(Keys.RETURN)
        time.sleep(3)

        # Wait for password input and enter password
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
        )
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)

        # Join the Google Meet
        driver.get(meet_link)
        time.sleep(10)

        # Turn off microphone and camera if not already turned off
        try:
            mic_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Turn off microphone (CTRL + D)']"))
            )
            mic_button.click()
        except Exception:
            print("Mic was already off or not found.")

        try:
            camera_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Turn off camera (CTRL + E)']"))
            )
            camera_button.click()
        except Exception:
            print("Camera was already off or not found.")

        # Join the meeting
        join_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Join now')]"))
        )
        join_button.click()
        time.sleep(5)

        # Monitor meeting duration
        print("Joined the meeting. Recording audio...")
        while True:
            try:
                # Check if "Leave call" button exists to verify the meeting is ongoing
                driver.find_element(By.XPATH, "//span[contains(text(),'Leave call')]")
                time.sleep(10)  # Check every 10 seconds
            except NoSuchElementException:
                print("Meeting has ended. Stopping recording...")
                break

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Stop FFmpeg recording if it was started
        if ffmpeg_process:
            print("Stopping audio recording...")
            ffmpeg_process.terminate()

        # Quit the browser
        driver.quit()
        print(f"Recording saved to {output_audio_file}")


# Streamlit Interface
st.title("Meeting Summarizer and Recorder Bot")
st.write("""
Upload a meeting link, audio, video, or PDF file, and we'll either summarize or record it for you.
If you have doubts even after reviewing the summary, use the text box for clarification.
""")

# Input Section
st.header("Upload Your Meeting Details")
input_type = st.radio(
    "Select Input Type:",
    ("Meeting Link", "Audio File", "Video File", "PDF File")
)

user_input = None

if input_type == "Meeting Link":
    user_input = st.text_input("Enter the Google Meet link:")
elif input_type == "Audio File":
    user_input = st.file_uploader("Upload an audio file:", type=["mp3", "wav", "m4a"])
elif input_type == "Video File":
    user_input = st.file_uploader("Upload a video file:", type=["mp4", "mkv", "avi"])
elif input_type == "PDF File":
    user_input = st.file_uploader("Upload a PDF file:", type=["pdf"])

# Clarification Section
st.header("Clarification Request")
clarification_text = st.text_area(
    "Type here if you were unable to perceive even from the summary notes:"
)

# Submit Button
if st.button("Submit"):
    if user_input:
        if input_type == "Meeting Link":
            st.info("The bot is now joining the meeting and recording it. Please wait...")
            try:
                join_and_record_meeting(
                    meet_link=user_input,
                    email="mayurkumark.ai23@rvce.edu.in",  # Replace with your bot's email
                    password="Knmk2715"        # Replace with your bot's password
                )
                st.success("The meeting has been successfully recorded!")
                st.write("Your recording will be available shortly.")
            except Exception as e:
                st.error(f"An error occurred while recording the meeting: {str(e)}")
        else:
            st.success("Your file has been uploaded successfully!")
            st.write("Processing your input...")

        if clarification_text:
            st.write("Your clarification request has been recorded:")
            st.write(clarification_text)
        else:
            st.info("No clarification request provided.")
    else:
        st.error("Please provide an input (link or file).")

# Footer
st.write("---")
st.write("Thank you for using the Meeting Summarizer and Recorder Bot!")
