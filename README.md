# 🎲 D&D Character Generator Web Interface

Uses ComfyUI + vision LLM to take a description of an uploaded picture and generate a Comfyui prompt using the character's stats and class, then describes the image and creates a background story for the character. 

Use a better Comfyui workflow for better results - This one uses IPadapters to do the faceswap and dreamshaper was fast enough for my testing purposes, I will be adding Qwen and higher quality image generation models soon. 

I'm uploading this as an example of how to use Comfyui + vision models to build automated prompt workflows. 
Granite3.2-vision uses tool calls to retrieve stats from the user input.

Check out comfydnd1 working.py for a single file implementation. 

Example : 
``` comfydnd1 working.py "description of what you want" /location/to/image```

## ✨ Features

### 🎭 Character Creation
- **Manual Mode**: Input your own character stats, name, and class
- **Auto Mode**: Just upload a photo and let AI randomly generate everything
- **Stat Rolling**: Use D&D 4d6 drop lowest mechanics with visual dice rolling
- **12 D&D Classes**: Choose from all core D&D classes

### 📸 Photo Integration
- **File Upload**: Upload photos from your device
- **Webcam Capture**: Take photos directly in the browser
- **Real-time Preview**: See your photo before generation

### 🎨 AI Image Generation
- **ComfyUI Integration**: Uses your existing ComfyUI setup
- **Face Recognition**: AI preserves your facial features in the fantasy character
- **Style Consistency**: Pixel art D&D character style
- **High Quality**: 512x512 PNG output with metadata

### 🖼️ Gallery System
- **Scrollable Gallery**: View all your generated characters
- **Download Options**: Save images individually
- **Modal View**: Click to enlarge images
- **Automatic Management**: Images sorted by creation date

## 🛠️ Setup Instructions

### Prerequisites
1. **Ollama** or open-ai compatible server running on remote server `0.0.0.0:11434` with models:
   - `llama3.1` (for character descriptions)
   - `granite3.2-vision` (for photo analysis)

2. **ComfyUI** running on remote server `100.111.66.29:8188` with:
   - Required models: `dreamshaper_8.safetensors`
   - Required LoRA: `pixelart_style_eagle_v6.safetensors`
   - IPAdapter models for face recognition
   - You need the custom_node comfyui_image_metadata_extension
   https://github.com/edelvarden/comfyui_image_metadata_extension

### Remote Server Configuration
The app is configured to use remote servers. If you need to change the server addresses, edit `config.py`:
```python
OLLAMA_HOST = "0.0.0.0:11434"
COMFYUI_HOST = "0.0.0.0:8188"
```

### Installation

1. **Clone/Navigate to the project directory**
   ```bash
   cd adventureBanana
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure remote services are running**
   - Ollama server on `0.0.0.0:11434`
   - ComfyUI server on `0.0.0.0:8188`

4. **Run the Flask application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 🎯 How to Use

### Manual Character Creation
1. Click **"Manual Entry"** mode
2. Upload a photo or use webcam
3. Enter character name and select class
4. Set ability scores manually or use dice rolling
5. Click **"Generate Character"**

### Auto Character Creation
1. Click **"Auto Generate"** mode
2. Upload a photo or use webcam
3. Click **"Generate Character"**
4. AI will randomly create stats, name, and class

### Gallery Features
- Generated images appear in the right sidebar
- Click any image to view larger
- Use download button to save images
- Gallery automatically updates with new generations

## 🔧 Configuration

### ComfyUI Output Directory
The app automatically searches for ComfyUI output in these locations:
- `/home/ut/3Git/ComfyUI/output`
- `./ComfyUI/output`
- `../ComfyUI/output`
- `~/ComfyUI/output`

### Ollama Configuration
Update these variables in `app.py` if needed:
```python
client = Client(host='0.0.0.0:11434')  # Ollama host
omodel = 'llama3.1'                    # Main model
```

### File Upload Settings
- Max file size: 16MB
- Supported formats: JPG, PNG, JPEG
- Upload directory: `./uploads`
- Generated images: `./generated`

## 🎨 Customization

### Styling
- CSS file: `static/css/style.css`
- Modern gradient design with responsive layout
- Customizable color scheme and animations

### ComfyUI Workflow
- Modify the workflow in the `create_comfyui_prompt()` function
- Current workflow includes:
  - Face ID preservation
  - Pixel art LoRA style
  - IPAdapter for face consistency
  - High-quality output settings

### Character Classes
Add or modify D&D classes in `app.py`:
```python
dnd_classes = ['Bard', 'Paladin', 'Rogue', ...] 
```

## 🚀 Advanced Features

### API Endpoints
- `GET /` - Main interface
- `POST /generate` - Character generation
- `GET /gallery` - Get generated images list
- `GET /generated/<filename>` - Serve generated images
- `GET /download/<filename>` - Download images

### JavaScript Features
- Real-time form validation
- Webcam integration with MediaDevices API
- AJAX form submission with loading states
- Dynamic gallery updates
- Modal image viewer

## 🐛 Troubleshooting

### Common Issues

**"No image provided" error**
- Ensure you've uploaded a photo or used webcam before generating

**ComfyUI connection failed**
- Check that ComfyUI is running on port 8188
- Verify all required models are installed

**Ollama model not found**
- Install required models: `ollama pull llama3.1` and `ollama pull granite3.2-vision`

**Image generation timeout**
- Increase `max_wait` parameter in `wait_for_generation()`
- Check ComfyUI logs for processing errors

### Performance Tips
- Use smaller images for faster processing
- Ensure sufficient GPU memory for ComfyUI
- Close unused browser tabs during generation

## 📁 File Structure
```
adventureBanana/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       └── script.js     # Client-side functionality
├── uploads/              # User uploaded photos
├── generated/            # AI generated images
└── README.md            # This file
```

## 🎮 Original Script Integration

This web interface is built on top of the existing `dndcomfymerge4.py` script, maintaining compatibility with:
- D&D stat generation mechanics
- Ollama character descriptions
- ComfyUI workflow and models
- Image processing pipeline

## 📝 License

This project builds upon existing D&D mechanics and integrates with open-source AI tools. Please ensure you have proper licenses for all ComfyUI models and LoRAs used.

---

Enjoy creating your D&D characters! 🧙‍♂️⚔️🐉
# ComfyAdventure
# ComfyAdventure
