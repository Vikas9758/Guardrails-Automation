# Parsing emails:
# https://stackoverflow.com/a/71167148
# https://stackoverflow.com/a/71151722
# https://stackoverflow.com/a/41748262
# https://stackoverflow.com/a/12468274
# https://stackoverflow.com/a/42495690

import email
from common import reduce_html, fetch_prompt, tokenizer

prompt_base = """I want you to act as a spam detector to determine whether a given
email is a phishing email or a legitimate email. Your analysis
should be thorough and evidence-based. Phishing emails often
impersonate legitimate brands and use social engineering techniques
to deceive users. These techniques include, but are not limited to:
fake rewards, fake warnings about account problems, and creating
a sense of urgency or interest. Spoofing the sender address and
embedding deceptive HTML links are also common tactics.

Analyze the email by following these steps:
1. Identify any impersonation of well-known brands.
2. Examine the email header for spoofing signs, such as
discrepancies in the sender name or email address.
Evaluate the subject line for typical phishing characteristics
(e.g., urgency, promise of reward). Note that the To address has
been replaced with a dummy address.
3. Analyze the email body for social engineering tactics designed to
induce clicks on hyperlinks. Inspect URLs to determine if they are
misleading or lead to suspicious websites.
4. Provide a comprehensive evaluation of the email, highlighting
specific elements that support your conclusion. Include a detailed
explanation of any phishing or legitimacy indicators found in the
email.
5. Summarize your findings and provide your final verdict on the
legitimacy of the email, supported by the evidence you gathered.

Your output should be JSON-formatted text with the following
keys:
- is_phishing: a boolean value indicating whether the email is
phishing (true) or legitimate (false)
- phishing_score: phishing risk confidence score as an integer on a
scale from 0 to 10
- brand_impersonated: brand name associated with the email, if
applicable
- rationales: detailed rationales for the determination, up to 500
words
- brief_reason: brief reason for the determination
Example output:
{
    "is_phishing": true,
    "phishing_score": 10,
    "brand_impersonated": "Google",
    "rationales": "The from address doesn't seem to belong to Google. There is a link in the email to a random domain. There is a sense of urgency common to phishing emails.",
    "brief_reason": "Seems to impersonate Google"
}

Email:
"""

def email_from_bytes(email_bytes):
    email_message = email.message_from_bytes(email_bytes)
    # Replace To with some email.
    if 'To' in email_message:
        del email_message['To']
    email_message['To'] = 'abc@gmail.com'

    header_text = ""
    # We first place important headers as we truncate the header text to 1500 tokens.
    important_headers = ['Received', 'Authentication-Results', 'From', 'To', 'Subject']
    for key in important_headers:
        if key in email_message:
            header_text += f"{key}: {email_message[key]}\n"
    for key in email_message:
        # TODO: Look into DMARC and DKIM headers.
        if key[0].lower() != 'x' and key != 'DKIM-Signature' and key not in important_headers:
            header_text += f"{key}: {email_message[key]} \n"
    header_text = tokenizer.decode(tokenizer.encode(header_text)[:1500])

    html_texts = []
    plain_texts = []
    for part in email_message.walk():
        content_type = part.get_content_type()
        content_charset = part.get_content_charset("utf-8")
        if content_type == "text/plain" or content_type == "text/html":
            payload = part.get_payload(decode=True)
            if payload:
                try:
                    payload_text = payload.decode(content_charset)
                except Exception:
                    payload_text = payload.decode('utf-8', errors='ignore')
                if content_type == "text/plain":
                    plain_texts.append(payload_text)
                else:
                    html_texts.append(payload_text)

    number_of_tokens = (len(tokenizer.encode(header_text))
        + sum([len(tokenizer.encode(text)) for text in plain_texts])
        + sum([len(tokenizer.encode(text)) for text in html_texts]))
    
    TOKEN_LIMIT = 3000
    if number_of_tokens > TOKEN_LIMIT:
        # Step 1: Remove plain text messages if we have html messages.
        if len(html_texts) > 0:
            while number_of_tokens > TOKEN_LIMIT and len(plain_texts) != 0:
                number_of_tokens -= len(tokenizer.encode(plain_texts.pop()))

        # Step 2: Reduce HTML
        for i in range(len(html_texts)):
            if number_of_tokens > TOKEN_LIMIT:
                number_of_tokens -= len(tokenizer.encode(html_texts[i]))
                html_texts[i] = reduce_html(html_texts[i], 0) # We set max_tokens to 0 so that it reduces as much as possible.
                number_of_tokens += len(tokenizer.encode(html_texts[i]))
        
        # Step 3: Deal with larger files by removing tokens from the middle.
        if number_of_tokens > TOKEN_LIMIT:
            extra_space = TOKEN_LIMIT - len(tokenizer.encode(header_text))
            tokens_per_file = extra_space // (len(html_texts) + len(plain_texts))
            for i in range(len(html_texts)):
                text = html_texts[i]
                tokens = tokenizer.encode(text)
                if len(tokens) > tokens_per_file:
                    tokens_to_keep = tokens[:tokens_per_file//2] + tokens[-tokens_per_file//2:]
                    html_texts[i] = tokenizer.decode(tokens_to_keep)
            for i in range(len(plain_texts)):
                text = plain_texts[i]
                tokens = tokenizer.encode(text)
                if len(tokens) > tokens_per_file:
                    tokens_to_keep = tokens[:tokens_per_file//2] + tokens[-tokens_per_file//2:]
                    plain_texts[i] = tokenizer.decode(tokens_to_keep)

    res = header_text
    res += "\n"
    res += "\n".join(html_texts)
    res += "\n"
    res += "\n".join(plain_texts)
    return res

def classify_email(email_bytes):
    return fetch_prompt(prompt_base + email_from_bytes(email_bytes))