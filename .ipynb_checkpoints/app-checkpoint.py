import playwright.sync_api
import streamlit as st
from website_classifier import classify_url
from email_classifier import classify_email
from sms_classifier import classify_message
from call_classifier import classify_call, classify_transcript, classify_youtube_url
import playwright
import json 

st.title("Phishing detection")

choice = st.selectbox("Object type:", ["URL", "Email", "SMS", "Call"])

if choice == "URL":
    url = st.text_input("URL")
    if st.button("Check URL"):
        try:
            st.table(json.loads(classify_url(url)))
        except playwright.sync_api.Error:
            st.write("Couldn't scrape the page.")
        except Exception:
            st.write("Couldn't classify the URL.")
elif choice == "Email":
    input_type = st.selectbox("Input type:", ["File", "Source"])
    if input_type == "File":
        email = st.file_uploader("Email", type=["eml"])
        if st.button("Check email"):
            if email == None:
                st.write("Please upload an email.")
            else:
                try:
                    email_bytes = email.getvalue()
                    st.table(json.loads(classify_email(email_bytes)))
                except Exception as e:
                    print(type(e), e)
                    st.write("Couldn't classify the email.")
    else:
        email = st.text_area("Email")
        if st.button("Check email"):
            try:
                st.table(json.loads(classify_email(email.encode())))
            except Exception:
                st.write("Couldn't classify the email.")
elif choice == "SMS":
    input_type = st.selectbox("Input type:", ["Source", "File"])
    if input_type == "Source":
        sms = st.text_area("SMS")
        if st.button("Check SMS"):
            try:
                st.table(json.loads(classify_message(sms)))
            except Exception:
                st.write("Couldn't classify the SMS.")
    else:
        sms = st.file_uploader("SMS", type=["txt"])
        if st.button("Check SMS"):
            if sms == None:
                st.write("Please upload a SMS.")
            else:
                try:
                    sms = sms.getvalue().decode()
                    st.table(json.loads(classify_message(sms)))
                except Exception:
                    st.write("Couldn't classify the SMS.")
elif choice == "Call":
    input_type = st.selectbox("Input type:", ["File", "Transcript", "Youtube link"])
    if input_type == "File":
        call = st.file_uploader("Call", type=["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"])
        if st.button("Check call"):
            if call == None:
                st.write("Please upload a call")
            else:
                try:
                    st.table(json.loads(classify_call(call.name, call.getvalue())))
                except Exception as e:
                    print(e)
                    st.write("Couldn't classify the call")
    elif input_type == "Transcript":
        transcript = st.text_area("Transcript")
        if st.button("Check transcript"):
            try:
                st.table(json.loads(classify_transcript(transcript)))
            except Exception:
                st.write("Couldn't classify the transcript")
    else:
        url = st.text_input('URL')
        if st.button("Check Youtube video"):
            try:
                st.table(json.loads(classify_youtube_url(url)))
            except Exception as e:
                st.write("Couldn't classify the video.")