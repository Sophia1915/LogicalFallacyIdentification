import os
import openai
import requests
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# List of logical fallacies

fallacies = [
    "ad hominem", "anecdotal evidence", "appeal to authority","appeal to emotion", "appeal to ignorance", "appeal to popularity","begging the question", "false cause", "personal incredulity", "tu quoque", "slippery slope", "straw man"
]


def generate_responses():
  # Get the API key from the environment variable
  api_key = os.getenv('API_KEY')

  if not api_key:
    raise ValueError("No API_KEY found in environment variables!")

  # Initialize the OpenAI API client
  openai.api_key = api_key

  # Define the API endpoint
  endpoint = "https://api.openai.com/v1/chat/completions"

  # Define the headers for the request
  headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_key}"
  }

  chosen_fallacy = random.choice(fallacies)

  # Define the user's questions using the chosen fallacy
  user_questions = [
      f"I am creating the backside of a flashcard. Provide one concise, vivid, and specific example of the {chosen_fallacy} fallacy being commited in a debate. Do not name the fallacy or provide any other additional information or explanation."
  ]

  # Create a list of message objects for the conversation
  messages = [{
      "role": "user",
      "content": question
  } for question in user_questions]

  # Define the payload data as a dictionary
  payload = {
      "model": "gpt-3.5-turbo",
      "messages": messages,
      "temperature": 0.7
  }

  # Make the API request
  response = requests.post(endpoint, headers=headers, json=payload)

  # Extract and return responses
  assistant_responses = []
  for i, choice in enumerate(response.json().get('choices', [])):
    assistant_response = choice['message']['content']
    assistant_responses.append(assistant_response)

  return assistant_responses, chosen_fallacy


def get_explanation(chosen_fallacy, example):
  # Get the API key from the environment variable
  api_key = os.getenv('API_KEY')

  # Define the API endpoint
  endpoint = "https://api.openai.com/v1/chat/completions"

  # Define the headers for the request
  headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_key}"
  }

  user_question = f"'{example}'. Concisely and clearly explain why this is a {chosen_fallacy} fallacy."

  # Create a message object for the conversation
  messages = [{"role": "user", "content": user_question}]

  # Define the payload data as a dictionary
  payload = {
      "model": "gpt-3.5-turbo",
      "messages": messages,
      "temperature": 0.6
  }

  # Make the API request
  response = requests.post(endpoint, headers=headers, json=payload)

  # Extract and return assistant response
  assistant_response = response.json().get('choices',
                                           [{}])[0].get('message',
                                                        {}).get('content', "")

  return assistant_response
