from common import fetch_prompt, tokenizer

prompt_base = """
You are a security expert tasked
with examining SMS messages to determine if it is a
phishing message or a legitimate message. To complete this
task, follow these sub-tasks:
1. Analyze the SMS for any SE techniques often used in
phishing attacks. Point out any suspicious behaviour.
2. Identify the brand name.
3. State your conclusion on whether the message is a
phishing message or a legitimate one, and explain your
reasoning. If there is insufficient evidence to make
a determination, answer "unknown".

Limitations:
- The message shortened and simplified.
Examples of social engineering techniques:
- Alerting the user to a problem with their account
- Offering unexpected rewards
- Informing the user of a missing package or additional
payment required
- Displaying fake security warnings

Submit your findings as an JSON object with the following keys:
- phishing_score: int (indicates phishing risk on a
scale of 0 to 10)
- brands: str (identified brand name or null if not
applicable)
- phishing: boolean (whether the message is a phishing
message or a legitimate message)
- reason: str (reason for your decision)
Note that JSON uses null, not None.
Example output:
{
    "phishing_score": 10,
    "brands": "Amazon",
    "phishing": true,
    "reason": "The message says that it's from Amazon, but it uses a suspicious URL."
}

Message:
"""

def classify_message(message):
    tokens = tokenizer.encode(message)
    if len(tokens) > 1000:
        message = tokenizer.decode(tokens[:500] + tokens[-500:])
    return fetch_prompt(prompt_base + message)