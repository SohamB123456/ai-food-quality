"""
Configuration file for the PokeWorks QA System
"""

import os

# OpenAI API Configuration
# Set your API key here or as an environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-api-key-here')

# Other configuration options
DEBUG = True
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

# GPT-4o model configuration
GPT_MODEL = "gpt-4o"
GPT_MAX_TOKENS = 1000
GPT_TEMPERATURE = 0.1
