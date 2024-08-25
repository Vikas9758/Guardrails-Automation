from common import fetch_prompt, fetch_transcript, tokenizer
import yt_dlp
import os

prompt_base = """
You are a phishing call detector and security expert tasked
with examining a phishing call to determine if it is a
phishing call or a legitimate call. To complete this
task, follow these sub-tasks:
1. Analyze the call transcript for any SE techniques
often used in phishing attacks.
2. Identify the brand name.
3. State your conclusion on whether the call is a
phishing call or a legitimate one, and explain your
reasoning. If there is insufficient evidence to make
a determination, answer "unknown".

Limitations:
- The call transcript may be shortened and simplified.
Examples of social engineering techniques:
- Alerting the user to a problem with their account
- Offering unexpected rewards
- Informing the user of a missing package or additional
payment required

Submit your findings as JSON-formatted output with
the following keys:
- phishing_score: int (indicates phishing risk on a
scale of 0 to 10)
- brands: str (identified brand name or null if not
applicable)
- phishing: boolean (whether the site is a phishing
site or a legitimate site)
- reason: str (reason for your decision)
Example output:
{
    "phishing_score": 10,
    "brands": "Amazon,
    "phishing": true,
    "reason": "The caller says that they're from Amazon and tells them to immediately transfer $10000 to a random bank account. It is unlikely that this is actually from Amazon."
}

Transcript:
"""

file_counter = 0

def classify_youtube_url(url):
    global file_counter
    file_counter += 1
    file_name = f'{file_counter}.m4a'
    print(file_name)
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': file_name,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }]
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download([url])
        print(error_code)
    try:
        with open(file_name, "rb") as f:
            res = classify_call(file_name, f.read())
        os.remove(file_name)
        return res
    except Exception as e:
        os.remove(file_name)
        raise e

def classify_transcript(transcript):
    tokens = tokenizer.encode(transcript)
    if len(tokens) > 4000:
        transcript = tokenizer.decode(tokens[:2000] + tokens[-2000:])
    return fetch_prompt(prompt_base + transcript)

def classify_call(filename, filebytes):
    transcript = fetch_transcript(filename, filebytes)
    return classify_transcript(transcript)