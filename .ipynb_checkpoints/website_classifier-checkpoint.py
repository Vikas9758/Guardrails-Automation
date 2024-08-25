from playwright.sync_api import sync_playwright
from paddleocr import PaddleOCR
import time
import asyncio
import sys
from PIL import Image
import io
import numpy as np
from common import reduce_html, fetch_prompt, tokenizer

# https://stackoverflow.com/a/42495690

ocr = PaddleOCR(use_angle_cls=True, lang='en')
# https://stackoverflow.com/a/76887425
# https://stackoverflow.com/a/44639711
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

def get_text_from_image(image, token_limit=500):
    try:
        ocr_result = ocr.ocr(image, cls=True)
        if len(ocr_result) > 0 and ocr_result[0] != None:
            ocr_result = ocr_result[0]
        else:
            ocr_result = []
        # Sort results by area of bounding box divided by number of characters.
        # This is an approximation for font size.
        ocr_result.sort(
            key = lambda res: (res[0][1][0] - res[0][0][0]) * (res[0][2][1] - res[0][0][1]) / len(res[1][0]),
            reverse=True
        )
        ocr_text = "\n".join([x[1][0] for x in ocr_result])
        ocr_text = tokenizer.decode(tokenizer.encode(ocr_text)[:token_limit])
        return ocr_text
    except Exception as e:
        return ""

prompt_base = """
You are a web programmer and security expert tasked
with examining a web page to determine if it is a
phishing site or a legitimate site. To complete this
task, follow these sub-tasks:
1. Analyze the HTML, URL, and OCR-extracted text from the
screenshot image for any SE techniques often used in
phishing attacks. Point out any suspicious elements
found in the HTML, URL, or text.
2. Identify the brand name. If the HTML appears to
resemble a legitimate web page, verify if the URL
matches the legitimate domain name associated with
the brand, if known.
3. State your conclusion on whether the site is a
phishing site or a legitimate one, and explain your
reasoning. If there is insufficient evidence to make
a determination, answer "unknown".

Limitations:
- The HTML may be shortened and simplified.
- The OCR-extracted text may not always be accurate.
Examples of social engineering techniques:
- Alerting the user to a problem with their account
- Offering unexpected rewards
- Informing the user of a missing package or additional
payment required
- Displaying fake security warnings
- Using a URL similar to the brand name, but with
some spelling mistakes, like appl.com instead of apple.com
If you get a Cloudflare warning or similar warning about the site being
a phishing site, classify the site as a phishing site.

Submit your findings as JSON-formatted output with
the following keys:
- phishing_score: int (indicates phishing risk on a
scale of 0 to 10)
- brands: str (identified brand name or null if not
applicable)
- phishing: boolean (whether the site is a phishing
site or a legitimate site)
- suspicious_domain: boolean (whether the domain name
is suspected to be not legitimate)
- reason: str (reason for your decision)
Example output:
{
    "phishing_score": 10,
    "brands": "Google",
    "phishing": true,
    "suspicious_domain": true,
    "reason": "The website looks like Google's website and has the same logo, but the URL isn't Google's."
}

"""

def classify_url(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        time.sleep(0.5)

        image_bytes = page.screenshot()
        image = np.asarray(Image.open(io.BytesIO(image_bytes)))
        final_url = page.url[:200]
        page_html = page.content()

        browser.close()

    page_html = reduce_html(page_html)
    image_text = get_text_from_image(image)

    prompt = prompt_base
    prompt += f"URL:\n{final_url}\n"
    prompt += f"HTML:\n``` {page_html} ```\n"
    prompt += f"Text extracted using OCR:\n``` {image_text} ```\n"

    return fetch_prompt(prompt)