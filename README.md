# Text Extraction from Images using Gemini API

## Introduction

This document outlines the process for extracting text from images using the Gemini API with the Google AI Python SDK. The steps include setting up the environment, configuring the Gemini API, uploading images, and generating the text content from the images.

## Prerequisites

1. Python 3.6 or later installed on your system.
2. A Google AI account with access to the Gemini API.
3. Internet connection to download the required Python packages and interact with the API.

## Steps

### 1. Install Google AI Python SDK

Install the Google AI Python SDK using pip:

```bash
$ pip install google-generativeai
```

For more information, refer to the [getting started guide](https://ai.google.dev/gemini-api/docs/get-started/python).

### 2. Configure Gemini API

First, import the required modules and configure the Gemini API with your API key:

```python
import os
import google.generativeai as genai

api = '<Gemini_Api_Key>'
genai.configure(api_key=api)
```

Replace `<Gemini_Api_Key>` with your actual Gemini API key.

### 3. Upload Images to Gemini

Create a function to upload images to the Gemini API:

```python
def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini.

    See https://ai.google.dev/gemini-api/docs/prompting_with_media
    """
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file
```

### 4. Configure the Generative Model

Configure the generative model with appropriate settings:

```python
generation_config = {
    "temperature": 0.9,
    "top_p": 0.95,
    "top_k": 32,
    "max_output_tokens": 1024,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.0-pro-vision-latest",
    generation_config=generation_config,
    # safety_settings = Adjust safety settings
    # See https://ai.google.dev/gemini-api/docs/safety-settings
)
```

### 5. Upload and Process Images

Upload the image file and process it to extract text:

```python
# TODO Make these files available on the local file system
# You may need to update the file paths
files = [
    upload_to_gemini("<image file location>", mime_type="image/png"),
]

response = model.generate_content([
    files[0],
    "extract the text from the image",
    "Image: extract the text from the image",
])

print(response.text)
```

Ensure that the file paths are correct and that the files are available on your local file system.

### 6. Run the Script

Run the script to upload the image and extract the text. The extracted text will be printed to the console.

input image : 

![image](https://github.com/SaiAkhileshP/Text-Extraction-from-Images-using-Gemini-API/assets/101054891/d5a149a9-784d-4ce8-9e30-ac1ec68a92f0)


Output image : 
![image](https://github.com/SaiAkhileshP/Text-Extraction-from-Images-using-Gemini-API/assets/101054891/08fd2398-3107-4450-9027-9e52924ac2c3)


## Conclusion

This document provides a step-by-step guide to extracting text from images using the Gemini API and the Google AI Python SDK. By following these steps, you can efficiently process images and extract their textual content for further analysis or use.

For more detailed information, refer to the [Gemini API documentation](https://ai.google.dev/gemini-api/docs).
