# example of how to use - python3.10 comfyAPIvision.py "description" 'path/to/image.jpg'

# set the path for the comfyui directory with output_dir

from urllib import request, parse
import random

import ollama
import sys


# file input 
import glob
import os 
import time
import json

# Get files before generation
output_dir = '/home/ut/3Git/ComfyUI/output'


prompt_text = """{
  "3": {
    "inputs": {
      "seed": 1016680605488490,
      "steps": 30,
      "cfg": 6.5,
      "sampler_name": "ddpm",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "21",
        0
      ],
      "positive": [
        "6",
        0
      ],
      "negative": [
        "7",
        0
      ],
      "latent_image": [
        "5",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "4": {
    "inputs": {
      "ckpt_name": "dreamshaper_8.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "5": {
    "inputs": {
      "width": 512,
      "height": 512,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "6": {
    "inputs": {
      "text": "pixel art, 8 bit style, Blue glasses.  Young woman rogue 33 years old wearing blue glasses wielding a stiletto dagger",
      "clip": [
        "34",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "7": {
    "inputs": {
      "text": "blurry, noisy, messy, lowres, jpeg, artifacts, ill, distorted, malformed, ",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "8": {
    "inputs": {
      "samples": [
        "3",
        0
      ],
      "vae": [
        "4",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "12": {
    "inputs": {
      "image": "IMG_4858.jpg"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "18": {
    "inputs": {
      "weight": 0.8000000000000002,
      "weight_faceidv2": -0.7700000000000001,
      "weight_type": "linear",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "20",
        0
      ],
      "ipadapter": [
        "20",
        1
      ],
      "image": [
        "12",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "20": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.5000000000000001,
      "provider": "CPU",
      "model": [
        "34",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  },
  "21": {
    "inputs": {
      "weight": 0.4000000000000001,
      "start_at": 0,
      "end_at": 1,
      "weight_type": "standard",
      "model": [
        "22",
        0
      ],
      "ipadapter": [
        "22",
        1
      ],
      "image": [
        "18",
        1
      ]
    },
    "class_type": "IPAdapter",
    "_meta": {
      "title": "IPAdapter"
    }
  },
  "22": {
    "inputs": {
      "preset": "FULL FACE - SD1.5 only (portraits stronger)",
      "model": [
        "18",
        0
      ],
      "ipadapter": [
        "20",
        1
      ]
    },
    "class_type": "IPAdapterUnifiedLoader",
    "_meta": {
      "title": "IPAdapter Unified Loader"
    }
  },
  "34": {
    "inputs": {
      "lora_name": "pixelart_style_eagle_v6.safetensors",
      "strength_model": 1.0000000000000002,
      "strength_clip": 1.0000000000000002,
      "model": [
        "4",
        0
      ],
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "Load LoRA"
    }
  },
    "37": {
            "inputs": {
              "filename_prefix": "ComfyUI",
              "subdirectory_name": "",
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
"""

def queue_prompt(prompt):
    p = {"prompt": prompt}
    data = json.dumps(p).encode('utf-8')
    req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
    request.urlopen(req)

def get_files_in_directory(directory):
    """Get all PNG files in directory with their creation times"""
    if not os.path.exists(directory):
        return {}
    
    files = {}
    for file_path in glob.glob(os.path.join(directory, "*.png")):
        files[file_path] = os.path.getctime(file_path)
    return files
n = str(sys.argv[1])


q = f'Create a descriptive prompt for image generation : Topic : {n}. Respond for a comfyui image generation. Your response is the prompt. Only reply being visually descriptive for the prompt. Respond in a single paragraph describing the image based on your command'

print(q)
## replace llama3.2-vision in 2 places with any ollama model you have. 

ollama.generate(model='llama3.2-vision', prompt=q)
response = ollama.chat(model='llama3.2-vision', messages=[
            {'role': 'user','content': q,},], keep_alive=0)
r1 = response['message']['content']

prompt = json.loads(prompt_text)
#set the text prompt for our positive CLIPTextEncode
prompt["6"]["inputs"]["text"] = r1

#set the seed for our KSampler node
prompt["3"]["inputs"]["seed"] = 5

#set image from user input
prompt["12"]["inputs"]["image"] = sys.argv[2]

print(r1)
print("Script name:", sys.argv[0])
print("Number of arguments:", len(sys.argv) - 1)
print("Arguments:", sys.argv[1:])

print(f"Checking output directory: {output_dir}")

files_before = get_files_in_directory(output_dir)
print(f"Files before generation: {len(files_before)}")

# Queue the prompt for generation
print("Queuing prompt for generation...")
queue_prompt(prompt)

# Wait for generation to complete and find new file
max_wait_time = 300  # 5 minutes maximum wait time
check_interval = 2   # Check every 2 seconds
waited_time = 0
latest_file = None

print("Waiting for image generation to complete...")

while waited_time < max_wait_time:
    files_after = get_files_in_directory(output_dir)
    
    # Find new files (files that weren't there before)
    new_files = []
    for file_path in files_after:
        if file_path not in files_before:
            new_files.append(file_path)
    
    if new_files:
        # Get the newest file among the new files
        latest_file = max(new_files, key=lambda x: files_after[x])
        print(f"Found new generated file: {latest_file}")
        break
    
    time.sleep(check_interval)
    waited_time += check_interval
    if waited_time % 10 == 0:  # Print status every 10 seconds
        print(f"Still waiting... ({waited_time}/{max_wait_time} seconds)")

if not latest_file:
    print(f"Error: No new files found in {output_dir} after waiting {max_wait_time} seconds")
    print("Please check:")
    print(f"1. ComfyUI is running and generating images to {output_dir}")
    print("2. The output directory path is correct")
    print("3. ComfyUI has sufficient time to generate the image")
    sys.exit(1)

# Verify the file exists
if not os.path.exists(latest_file):
    print(f"Error: File {latest_file} does not exist")
    sys.exit(1)

print(f"Successfully found generated image: {latest_file}")



ollama.generate(model='llama3.2-vision', prompt=q)
response2 = ollama.chat(model='llama3.2-vision', messages=[
            {'role': 'user','content': 'describe this image', 'images':[latest_file],},], keep_alive=0)
           
r2 = response2['message']['content']
print(r2)

