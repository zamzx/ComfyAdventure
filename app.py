from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
import json
import random
import time
import glob
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import d20
from ollama import chat, Client
import sys
from urllib import request as urllib_request, parse
import shutil
import requests
import config

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['GENERATED_FOLDER'] = config.GENERATED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_UPLOAD_SIZE

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

# Initialize Ollama client
client = Client(host=config.OLLAMA_HOST)
omodel = config.OLLAMA_MAIN_MODEL

# Local ComfyUI output directory used for filesystem-based watching and gallery
COMFY_OUTPUT_DIR = '/home/ut/3Git/ComfyUI/output/adventure'

# D&D Classes
dnd_classes = ['Bard', 'Paladin', 'Rogue', 'Wizard', 'Fighter', 'Cleric', 'Druid', 'Ranger', 'Barbarian', 'Monk', 'Sorcerer', 'Warlock']

class Character:
    def __init__(self):
        self.stats = {'Strength': 0, 'Dexterity': 0, 'Constitution': 0, 'Intelligence': 0, 'Wisdom': 0, 'Charisma': 0}
        self.name = ""
        self.character_class = ""
        self.user_description = ""

        
    def roll_stats(self):
        """Roll 4d6 drop lowest for each stat"""
        for stat in self.stats:
            self.stats[stat] = d20.roll("4d6").total
        return self.stats
    
    def random_stats(self):
        """Generate random but balanced stats"""
        for stat in self.stats:
            self.stats[stat] = random.randint(8, 18)
        return self.stats

def analyze_image_with_vision(image_path):
    """Use vision model to analyze uploaded image"""
    try:
        vision_response = client.chat(
            model=config.OLLAMA_VISION_MODEL, 
            messages=[{
                'role': 'user',
                'content': 'Describe the person in this image. Take great care to describe the hair, face, and body. Ignore the background and surroundings.',
                'images': [image_path]
            }],
            keep_alive=0
        )
        return vision_response['message']['content']
    except Exception as e:
        print(f"Vision analysis error: {e}")
        return "A person with distinctive features suitable for a fantasy character."

def generate_character_description(character):
    """Generate character description using Ollama"""
    try:
        messages = [{
            'role': 'user', 
            'content': f'''Create a detailed visual description for D&D character generation:
            Name: {character.name}
            Class: {character.character_class}
            Stats: {character.stats}
            Physical Description: {character.user_description}
            
            Describe the character with appropriate equipment, pose, and adventuring style for their class. 
            Include details about armor, weapons, magic items, and setting that would make a great fantasy portrait.
            '''
        }]
        
        response = client.chat(omodel, messages=messages)
        return response.message.content
    except Exception as e:
        print(f"Character description error: {e}")
        return f"A {character.character_class} named {character.name} with the described physical features."

def upload_image_to_comfyui(image_path, comfyui_host=None):
    """Upload image to ComfyUI server"""
    if not comfyui_host:
        comfyui_host = config.COMFYUI_HOST
    try:
        with open(image_path, 'rb') as f:
            files = {'image': (os.path.basename(image_path), f, 'image/png')}
            response = requests.post(f"http://{comfyui_host}/upload/image", files=files)
            if response.status_code == 200:
                result = response.json()
                return result.get('name', os.path.basename(image_path))
            else:
                print(f"Failed to upload image: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"Error uploading image to ComfyUI: {e}")
        return None

def queue_comfyui_prompt(prompt_data):
    """Queue prompt to ComfyUI"""
    try:
        p = {"prompt": prompt_data}
        data = json.dumps(p).encode('utf-8')
        req = urllib_request.Request(f"http://{config.COMFYUI_HOST}/prompt", data=data)
        urllib_request.urlopen(req)
        return True
    except Exception as e:
        print(f"ComfyUI queue error: {e}")
        return False

def get_latest_generated_image(output_dir=None):
    """Get the latest generated image from ComfyUI output directory"""
    if not output_dir:
        # Try to find ComfyUI output directory
        possible_dirs = [
            '/home/ut/3Git/ComfyUI/output',
            './ComfyUI/output',
            '../ComfyUI/output',
            os.path.expanduser('~/ComfyUI/output')
        ]
        
        for dir_path in possible_dirs:
            if os.path.exists(dir_path):
                output_dir = dir_path
                break
        
        if not output_dir:
            return None
    
    if not os.path.exists(output_dir):
        return None
    
    png_files = glob.glob(os.path.join(output_dir, "*.png"))
    if not png_files:
        return None
    
    # Get the most recent file
    latest_file = max(png_files, key=os.path.getctime)
    return latest_file

def get_files_in_directory(output_dir):
    """Return a dict of file_path -> ctime for PNG files in a directory."""
    files_map = {}
    try:
        for path in glob.glob(os.path.join(output_dir, '*.png')):
            try:
                files_map[path] = os.path.getctime(path)
            except Exception:
                continue
    except Exception as e:
        print(f"[DEBUG] Error reading directory {output_dir}: {e}")
    return files_map

def log_comfyui_directory_state(note=None):
    """Print helpful debug info about ComfyUI outputs and local state."""
    try:
        if note:
            print(f"[DEBUG] {note}")
        # Attempt to list local ComfyUI output directories (if accessible on this machine)
        possible_dirs = [
            '/home/ut/3Git/ComfyUI/output',
            './ComfyUI/output',
            '../ComfyUI/output',
            os.path.expanduser('~/ComfyUI/output')
        ]
        for dir_path in possible_dirs:
            exists = os.path.exists(dir_path)
            print(f"[DEBUG] Checking local path: {dir_path} exists={exists}")
            if exists:
                try:
                    files = sorted(glob.glob(os.path.join(dir_path, '*.png')))
                    tail = files[-10:]
                    print(f"[DEBUG] Local output png count: {len(files)}; last 10: {[os.path.basename(f) for f in tail]}")
                except Exception as e:
                    print(f"[DEBUG] Error listing {dir_path}: {e}")
    except Exception as e:
        print(f"[DEBUG] Error in log_comfyui_directory_state: {e}")

@app.route('/')
def index():
    return render_template('index.html', dnd_classes=dnd_classes)

@app.route('/generate', methods=['POST'])
def generate_character():
    try:
        # Get form data
        generation_type = request.form.get('generation_type', 'manual')
        character = Character()
        
        # Handle file upload
        uploaded_file = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename != '':
                filename = f"{int(time.time())}_{file.filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_file = filepath
        
        # Handle webcam data
        webcam_data = request.form.get('webcam_data')
        if webcam_data and webcam_data != '':
            # Decode base64 image
            image_data = base64.b64decode(webcam_data.split(',')[1])
            filename = f"webcam_{int(time.time())}.png"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(filepath, 'wb') as f:
                f.write(image_data)
            uploaded_file = filepath
        
        if not uploaded_file:
            return jsonify({'error': 'No image provided'}), 400
        
        # Analyze image with vision model
        character.user_description = analyze_image_with_vision(uploaded_file)
        
        if generation_type == 'manual':
            # Get manual stats from form
            character.name = request.form.get('name', f'Hero_{int(time.time())}')
            character.character_class = request.form.get('character_class', random.choice(dnd_classes))
            character.stats = {
                'Strength': int(request.form.get('strength', 10)),
                'Dexterity': int(request.form.get('dexterity', 10)),
                'Constitution': int(request.form.get('constitution', 10)),
                'Intelligence': int(request.form.get('intelligence', 10)),
                'Wisdom': int(request.form.get('wisdom', 10)),
                'Charisma': int(request.form.get('charisma', 10))
            }
        else:
            # Random generation
            character.name = f'Hero_{int(time.time())}'
            character.character_class = random.choice(dnd_classes)
            character.random_stats()
        
        # Upload image to ComfyUI server first
        uploaded_image_name = upload_image_to_comfyui(uploaded_file)
        if not uploaded_image_name:
            return jsonify({'error': 'Failed to upload image to ComfyUI server'}), 500
        
        # Generate character description
        description = generate_character_description(character)
        
        # Create ComfyUI prompt using the uploaded image name
        comfy_prompt = create_comfyui_prompt(description, uploaded_image_name)
        
        # Queue to ComfyUI
        if queue_comfyui_prompt(comfy_prompt):
            # Wait for generation and get result via filesystem
            generated_image_filename = wait_for_generation()
            
            if generated_image_filename:
                return jsonify({
                    'success': True,
                    'character': {
                        'name': character.name,
                        'class': character.character_class,
                        'stats': character.stats,
                        'description': description
                    },
                    'generated_image': generated_image_filename
                })
            else:
                return jsonify({'error': 'Image generation failed or timed out'}), 500
        else:
            return jsonify({'error': 'Failed to queue generation'}), 500
            
    except Exception as e:
        print(f"Generation error: {e}")
        return jsonify({'error': str(e)}), 500

def create_comfyui_prompt(description, image_name):
    """Create ComfyUI prompt based on the existing workflow"""
    # Use the full workflow from the original script
    prompt_template = {
        "3": {
            "inputs": {
                "seed": random.randint(1, 1000000),
                "steps": 45,
                "cfg": 6.5,
                "sampler_name": "ddpm",
                "scheduler": "karras",
                "denoise": 1,
                "model": ["21", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler",
            "_meta": {"title": "KSampler"}
        },
        "4": {
            "inputs": {
                "ckpt_name": "dreamshaper_8.safetensors"
            },
            "class_type": "CheckpointLoaderSimple",
            "_meta": {"title": "Load Checkpoint"}
        },
        "5": {
            "inputs": {
                "width": 512,
                "height": 512,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage",
            "_meta": {"title": "Empty Latent Image"}
        },
        "6": {
            "inputs": {
                "text": description,
                "clip": ["34", 1]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "CLIP Text Encode (Prompt)"}
        },
        "7": {
            "inputs": {
                "text": "blurry, noisy, messy, lowres, jpeg, artifacts, ill, distorted, malformed",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "CLIP Text Encode (Prompt)"}
        },
        "8": {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            },
            "class_type": "VAEDecode",
            "_meta": {"title": "VAE Decode"}
        },
        "12": {
            "inputs": {
                "image": image_name
            },
            "class_type": "LoadImage",
            "_meta": {"title": "Load Image"}
        },
        "18": {
            "inputs": {
                "weight": 0.8,
                "weight_faceidv2": -0.77,
                "weight_type": "linear",
                "combine_embeds": "concat",
                "start_at": 0,
                "end_at": 1,
                "embeds_scaling": "V only",
                "model": ["20", 0],
                "ipadapter": ["20", 1],
                "image": ["12", 0]
            },
            "class_type": "IPAdapterFaceID",
            "_meta": {"title": "IPAdapter FaceID"}
        },
        "20": {
            "inputs": {
                "preset": "FACEID PLUS V2",
                "lora_strength": 0.5,
                "provider": "CPU",
                "model": ["34", 0]
            },
            "class_type": "IPAdapterUnifiedLoaderFaceID",
            "_meta": {"title": "IPAdapter Unified Loader FaceID"}
        },
        "21": {
            "inputs": {
                "weight": 0.4,
                "start_at": 0,
                "end_at": 1,
                "weight_type": "standard",
                "model": ["22", 0],
                "ipadapter": ["22", 1],
                "image": ["18", 1]
            },
            "class_type": "IPAdapter",
            "_meta": {"title": "IPAdapter"}
        },
        "22": {
            "inputs": {
                "preset": "FULL FACE - SD1.5 only (portraits stronger)",
                "model": ["18", 0],
                "ipadapter": ["20", 1]
            },
            "class_type": "IPAdapterUnifiedLoader",
            "_meta": {"title": "IPAdapter Unified Loader"}
        },
        "34": {
            "inputs": {
                "lora_name": "pixelart_style_eagle_v6.safetensors",
                "strength_model": 1.0,
                "strength_clip": 1.0,
                "model": ["4", 0],
                "clip": ["4", 1]
            },
            "class_type": "LoraLoader",
            "_meta": {"title": "Load LoRA"}
        },
         "37": {
            "inputs": {
              "filename_prefix": "ComfyUI",
              "subdirectory_name": "adventure",
              "output_format": "png",
                "quality": "max",
                "metadata_scope": "full",
                "include_batch_num": "true",
                "prefer_nearest": "true",
                "images": ["8",0]
                 },
    "class_type": "SaveImageWithMetaData",
    "_meta": {
      "title": "Save Image With MetaData"
          }
    }
}
    return prompt_template

def get_comfyui_history(comfyui_host=None):
    """Get ComfyUI generation history"""
    if not comfyui_host:
        comfyui_host = config.COMFYUI_HOST
    try:
        response = requests.get(f"http://{comfyui_host}/history")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error getting ComfyUI history: {e}")
        return None

def download_generated_image(filename, subfolder=None, image_type=None, comfyui_host=None):
    """Download generated image from ComfyUI server using filename, and optional subfolder/type."""
    if not comfyui_host:
        comfyui_host = config.COMFYUI_HOST
    try:
        params = {'filename': filename}
        if subfolder is not None:
            params['subfolder'] = subfolder
        if image_type is not None:
            params['type'] = image_type
        response = requests.get(f"http://{comfyui_host}/view", params=params)
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

def wait_for_generation(max_wait=None):
    """Wait for ComfyUI to generate an image by polling the local output dir and return the filename."""
    if not max_wait:
        max_wait = config.MAX_WAIT_TIME

    output_dir = COMFY_OUTPUT_DIR
    if not os.path.exists(output_dir):
        print(f"[DEBUG] Output dir not found locally: {output_dir}")
        return None

    files_before = get_files_in_directory(output_dir)
    print(f"[DEBUG] Watching ComfyUI output dir: {output_dir}; baseline files: {len(files_before)}")

    waited = 0
    while waited < max_wait:
        time.sleep(2)
        waited += 2

        files_after = get_files_in_directory(output_dir)
        new_files = [p for p in files_after.keys() if p not in files_before]
        if new_files:
            latest_file = max(new_files, key=lambda x: files_after[x])
            print(f"[DEBUG] FS watcher found new generated file: {latest_file}")
            return os.path.basename(latest_file)

        if waited % 10 == 0:  # Print status every 10 seconds
            print(f"Still waiting for generation... ({waited}/{max_wait} seconds)")

    print("Generation timeout - no new images found")
    return None

@app.route('/gallery')
def gallery():
    """Get list of generated images directly from ComfyUI output directory."""
    images = []
    if os.path.exists(COMFY_OUTPUT_DIR):
        for filename in os.listdir(COMFY_OUTPUT_DIR):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                images.append(filename)
        images.sort(key=lambda x: os.path.getctime(os.path.join(COMFY_OUTPUT_DIR, x)), reverse=True)
    return jsonify({'images': images})

@app.route('/generated/<filename>')
def serve_generated_image(filename):
    """Serve generated images from ComfyUI output directory."""
    return send_file(os.path.join(COMFY_OUTPUT_DIR, filename))

@app.route('/download/<filename>')
def download_image(filename):
    """Download generated image from ComfyUI output directory."""
    return send_file(os.path.join(COMFY_OUTPUT_DIR, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

