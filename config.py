# Configuration file for D&D Character Generator

# Server Configuration
OLLAMA_HOST = "0.0.0.0:11434"
COMFYUI_HOST = "0.0.0.0:8188"

# Models
OLLAMA_MAIN_MODEL = "llama3.1"
OLLAMA_VISION_MODEL = "granite3.2-vision"

# Generation Settings
MAX_WAIT_TIME = 120  # seconds to wait for image generation
IMAGE_UPLOAD_TIMEOUT = 30  # seconds for image upload

# File Settings
MAX_UPLOAD_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Directory Settings
UPLOAD_FOLDER = 'uploads'
GENERATED_FOLDER = '/home/ut/3Git/ComfyUI/output'
