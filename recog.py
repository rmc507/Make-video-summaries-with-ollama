import requests
import json
import base64

# Define the image file path and the prompt
# image_file_path = r"C:\Users\rmcne\Pictures\Screenshots\Screenshot 2024-12-31 210658.png"
prompt = "Describe image in great detail. do not output more than two sentences. More than two sentinces is invalid."

# System message for character description
system_message = "Your task is to describe a frame of police bodycam breifly:  For people, use only male/female and notable identifiers, and describe the environment in no more than two sentences. Make sure to describe the people in detail. Do not make comments on image quality. the cameras point of veiw is the same as the police officers. Do not assume what the officer is doing. Simply say 'the officer observes'. If you cannot confidently dicern what the picture is simply respond 'unable to analyse frame'"

def describe_frame(encoded_image):
    # Open the image file and read its content
    #with open(image_file_path, "rb") as image_file:
    #    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    # Construct the data for the POST request
    data = {
        "model": "llava",
        "prompt": prompt,
        "system": system_message,
        "images": [encoded_image],
        "stream": False,
        "tempurature": '.5'
    }

    # Send the POST request
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post("http://localhost:11434/api/generate", json=data, headers=headers)
        response.raise_for_status()

        # Parse the JSON response and extract the 'response' field
        response_data = response.json()
        return response_data.get("response", "No response field in the API response")

    except requests.RequestException as e:
        return f"An error occurred: {e}"
    except json.JSONDecodeError:
        return "Error decoding JSON from the API response"


# Call the function with the image file path
# print(describe_frame(image_file_path))
