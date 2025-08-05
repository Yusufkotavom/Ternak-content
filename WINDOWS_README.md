# Auto Content Generator - Windows Guide

## 🚀 Quick Start for Windows

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

#### Option 1: Automatic Installation (Recommended)
1. Download the project files
2. Open Command Prompt in the project directory
3. Run the installer:
```cmd
install_windows.bat
```

#### Option 2: Manual Installation
1. Install dependencies:
```cmd
pip install -r requirements.txt
```

2. Create directories:
```cmd
mkdir output
mkdir output\images
mkdir templates
mkdir static
```

3. Copy environment file:
```cmd
copy .env.example .env
```

4. Edit `.env` file with your API keys

### Configuration

Edit the `.env` file and add your API keys:

```env
# Free AI APIs (Choose one or more)
COHERE_API_KEY=your_cohere_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
HUGGINGFACE_TOKEN=your_huggingface_token_here

# Image APIs (Free tiers available)
UNSPLASH_API_KEY=your_unsplash_key_here
PIXABAY_API_KEY=your_pixabay_key_here
PEXELS_API_KEY=your_pexels_key_here
```

### Free API Keys

Get free API keys from:
- **Cohere**: https://cohere.ai/ (Free tier available)
- **Anthropic**: https://anthropic.com/ (Free tier available)
- **HuggingFace**: https://huggingface.co/ (Free)
- **Unsplash**: https://unsplash.com/developers (Free tier)
- **Pixabay**: https://pixabay.com/api/docs/ (Free tier)
- **Pexels**: https://www.pexels.com/api/ (Free tier)

### Testing

Run Windows compatibility test:
```cmd
python test_windows.py
```

Run full system test:
```cmd
python test_system.py
```

### Running the Application

Start the web interface:
```cmd
python run.py
```

Or start directly:
```cmd
python main.py
```

Access the application:
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Usage

#### Web Interface
1. Open http://localhost:8000 in your browser
2. Enter keywords (one per line or upload CSV file)
3. Click "Generate Content"
4. View and download generated content

#### Command Line
```cmd
python cli.py --keyword "your keyword"
```

#### API
```cmd
curl -X POST "http://localhost:8000/process-keywords" \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["your keyword"]}'
```

### Troubleshooting

#### Common Issues

1. **Import Errors**
   ```cmd
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Port Already in Use**
   - Change port in `.env` file: `PORT=8001`
   - Or kill process using port 8000

3. **API Key Errors**
   - Check your `.env` file
   - Verify API keys are correct
   - Ensure at least one AI API is configured

4. **Directory Errors**
   ```cmd
   mkdir output
   mkdir output\images
   mkdir templates
   mkdir static
   ```

#### Testing Individual Components

Test imports:
```cmd
python -c "import fastapi, uvicorn, pandas, requests, aiohttp; print('All imports successful')"
```

Test configuration:
```cmd
python -c "from src.utils.config import Settings; s = Settings(); print('Configuration loaded')"
```

### File Structure

```
auto-content-generator/
├── main.py                 # Main application
├── run.py                  # Run script
├── cli.py                  # Command line interface
├── test_windows.py         # Windows compatibility test
├── test_system.py          # Full system test
├── install_windows.bat     # Windows installer
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── .env                   # Your configuration (create this)
├── output/                # Generated content
├── templates/             # HTML templates
├── static/                # Static files
└── src/                   # Source code
    ├── modules/           # Core modules
    └── utils/             # Utilities
```

### Features

✅ **Windows Compatible**
- No Docker required
- Works on Windows 10/11
- Simple installation

✅ **Free AI APIs**
- Cohere (free tier)
- Anthropic (free tier)
- HuggingFace (free)
- OpenAI (paid, optional)

✅ **Free Image APIs**
- Unsplash (free tier)
- Pixabay (free tier)
- Pexels (free tier)

✅ **Content Generation**
- E-E-A-T optimized content
- SEO-friendly articles
- HTML output
- WordPress publishing

✅ **Bulk Processing**
- CSV file upload
- Multiple keywords
- Batch processing

### Support

If you encounter issues:
1. Run `python test_windows.py` to check compatibility
2. Check the error messages
3. Verify your API keys
4. Ensure all directories exist

### Performance Tips

1. **For better performance:**
   - Use SSD storage
   - Close other applications
   - Use wired internet connection

2. **For large batches:**
   - Process keywords in smaller batches
   - Monitor memory usage
   - Use the CLI for bulk processing

### Security

- Keep your API keys secure
- Don't share your `.env` file
- Use HTTPS in production
- Regularly update dependencies

---

**Happy Content Generating! 🚀**