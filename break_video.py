
import cv2
import base64
import os
import requests
from recog import describe_frame

GROQ_API_KEY = "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"


# Global system message
SYSTEM_MESSAGE = "You are a summarization expert. Follow the summarization instructions exactly."

'''   # using ollama
def send_to_ollama(prompt):
    """
    Sends the combined text to the Ollama API and returns the response.
    """
    selected_model = 'qwen2.5-coder:latest' #"mistral:latest"
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    
    data = {
        "model": selected_model,
        "prompt": f"system: {SYSTEM_MESSAGE}\nuser: {prompt}\nassistant:",
        "stream": False,
        "tempurature": "2"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json().get("response", "No response received.")
    except requests.RequestException as e:
        print(f"Error communicating with Ollama: {e}")
        return None
'''
# using groq

def send_to_ollama(prompt):
    """
    Sends a prompt to the Groq API and returns the response.
    """
    model = "llama-3.3-70b-versatile"
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"  # Replace with your actual API key
    }
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response received.")
    except requests.RequestException as e:
        print(f"Error communicating with Groq API: {e}")
        return None


















def process_video_frames(video_path, num_frames):
    """
    Processes the specified number of frames from the video and generates summaries.
    """
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return None

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return None

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_rate = cap.get(cv2.CAP_PROP_FPS)  # Get frames per second (FPS)
    frame_interval = max(total_frames // num_frames, 1)
    frame_summaries = []

    print(f"Processing video: {video_path} with {total_frames} frames.")
    for frame_index in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            print(f"Error: Could not read frame {frame_index}.")
            break

        if frame_index % frame_interval == 0:
            _, buffer = cv2.imencode('.jpg', frame)
            encoded_frame = base64.b64encode(buffer).decode('utf-8')

            frame_description = describe_frame(encoded_frame)
            if not frame_description:
                print(f"Warning: No description generated for frame {frame_index}.")
                continue

            # Calculate the timestamp based on frame index and frame rate
            frame_time = (frame_index / frame_rate)  # Time in seconds

            # Convert frame_time to minutes and seconds
            minutes = int(frame_time // 60)
            seconds = int(frame_time % 60)
            timestamp_str = f"{minutes:02d}:{seconds:02d}"

            frame_summaries.append(f"Frame {frame_index + 1}/{total_frames} TIMESTAMP:({timestamp_str}) DESCRIPTION: {frame_description}")
            print(f"Processed frame {frame_index + 1}/{total_frames} at {timestamp_str}")
            
            if len(frame_summaries) >= num_frames:
                break

    cap.release()
    return frame_summaries

def read_additional_file(file_path):
    """
    Reads the contents of the additional file and returns it.
    """
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: Additional file not found at {file_path}")
    except IOError as e:
        print(f"Error reading additional file: {e}")
    return None

'''
def summarize_video(video_path, num_frames, additional_file, additional_context):
    """
    Combines frame summaries and additional content, sends them to Ollama, and returns the response.
    """
    # Process video frames
    frame_summaries = process_video_frames(video_path, num_frames)
    if not frame_summaries:
        print("Error: No frame summaries generated.")
        return None

    # Read additional file content
    additional_content = read_additional_file(additional_file)
    if not additional_content:
        print("Error: Additional content could not be read.")
        return None

    # Combine content
    combined_text = additional_content + "\nHere is some additional context:" + additional_content + "\n Here is the frame summaries".join(frame_summaries)
    print("Generating summary.")
    
    # Send to Ollama
    response = send_to_ollama(combined_text)
    if not response:
        print("Error: No response from Ollama.")
        return None

    return response
'''
def summarize_video(video_path, num_frames, additional_file, additional_context):
    """
    Combines frame summaries and additional content, sends them to Ollama, and returns the response.

    Args:
        video_path (str): Path to the video file.
        num_frames (int): Number of frames to process for summaries.
        additional_file (str): Path to the file containing additional content.
        additional_context (str): Additional context to include in the summary.

    Returns:
        str: Response from Ollama or None if an error occurs.
    """
    # Process video frames
    try:
        frame_summaries = process_video_frames(video_path, num_frames)
        if not frame_summaries:
            print("Error: No frame summaries generated.")
            return None
    except Exception as e:
        print(f"Error processing video frames: {e}")
        return None

    # Read additional file content
    try:
        with open(additional_file, 'r', encoding='utf-8') as file:
            additional_content = file.read()
    except FileNotFoundError:
        print(f"Error: File not found - {additional_file}")
        return None
    except Exception as e:
        print(f"Error reading additional file: {e}")
        return None

    # Combine content
    combined_text = (
        additional_content +
        "\n\nHere is some additional context:\n" +
        additional_context +
        "\n\nHere are the frame summaries:\n" +
        "\n".join(frame_summaries)
    )

    print("Generating summary...")

    # Send to Ollama
    try:
        response = send_to_ollama(combined_text)
        if not response:
            print("Error: No response from Ollama.")
            return None
    except Exception as e:
        print(f"Error sending to Ollama: {e}")
        return None

    return response

