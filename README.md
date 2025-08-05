# Auto Content Generator with E-E-A-T + Bulk Keyword Input

Sistem otomatisasi content generation dengan E-E-A-T (Experience, Expertise, Authority, Trust) dan bulk keyword input. Mendukung Windows, Linux, dan Mac dengan free AI APIs.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (Windows, Linux, Mac)
- pip (Python package installer)

### Installation

#### Windows (Recommended)
```cmd
# Run the Windows installer
install_windows.bat

# Or manual installation
pip install -r requirements.txt
```

#### Linux/Mac
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Copy environment file:
```bash
cp .env.example .env
```

2. Edit `.env` file with your API keys:
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

```bash
# Test Windows compatibility
python test_windows.py

# Test full system
python test_system.py

# Test app functionality
python test_app.py
```

### Running the Application

```bash
# Start the web interface
python run.py

# Or start directly
python main.py
```

Access the application:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📋 Features

### ✅ Core Features
- **Bulk Keyword Input** (CSV/textarea)
- **Automated Keyword Research**
- **E-E-A-T Content Generation**
- **AI Image Generation**
- **WordPress Publishing**
- **Web Interface**
- **CLI Tool**
- **API Endpoints**

### ✅ Platform Support
- **Windows Compatible** (No Docker required)
- **Linux/Mac Support**
- **Cross-platform**

### ✅ Free AI APIs
- **Cohere** (free tier)
- **Anthropic** (free tier)
- **HuggingFace** (free)
- **OpenAI** (paid, optional)

### ✅ Free Image APIs
- **Unsplash** (free tier)
- **Pixabay** (free tier)
- **Pexels** (free tier)

## 🎯 Usage

### Web Interface
1. Open http://localhost:8000 in your browser
2. Enter keywords (one per line or upload CSV file)
3. Click "Generate Content"
4. View and download generated content

### Command Line
```bash
python cli.py --keyword "your keyword"
```

### API
```bash
curl -X POST "http://localhost:8000/process-keywords" \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["your keyword"]}'
```

## 📁 Project Structure

```
auto-content-generator/
├── main.py                 # Main application
├── run.py                  # Run script
├── cli.py                  # Command line interface
├── test_windows.py         # Windows compatibility test
├── test_system.py          # Full system test
├── test_app.py             # App functionality test
├── install_windows.bat     # Windows installer
├── requirements.txt        # Python dependencies
├── requirements_minimal.txt # Minimal dependencies
├── .env.example           # Environment template
├── .env                   # Your configuration (create this)
├── output/                # Generated content
├── templates/             # HTML templates
├── static/                # Static files
└── src/                   # Source code
    ├── modules/           # Core modules
    │   ├── keyword_research.py
    │   ├── content_generator.py
    │   ├── image_generator.py
    │   └── wordpress_publisher.py
    └── utils/             # Utilities
        └── config.py
```

## 🔧 Modules

### Keyword Research (`src/modules/keyword_research.py`)
- Google Suggest API integration
- Related keywords extraction
- Competition analysis
- Search volume estimation
- Windows compatible (no Selenium)

### Content Generator (`src/modules/content_generator.py`)
- E-E-A-T optimized content
- Multiple AI API support (OpenAI, Cohere, Anthropic, HuggingFace)
- SEO-friendly articles
- HTML output generation
- Fallback mechanisms

### Image Generator (`src/modules/image_generator.py`)
- Free AI image generation (HuggingFace)
- Stock photo APIs (Unsplash, Pixabay, Pexels)
- Image optimization
- Local storage

### WordPress Publisher (`src/modules/wordpress_publisher.py`)
- WordPress REST API integration
- Media upload
- Post publishing
- Category management

## 🌐 API Endpoints

- `GET /` - Web interface
- `GET /health` - Health check
- `GET /api/status` - Application status
- `GET /api/test-ai` - Test AI APIs
- `POST /upload-keywords` - Upload CSV file
- `POST /process-keywords` - Process keywords
- `POST /publish-wordpress` - Publish to WordPress

## 🛠️ Configuration

### Environment Variables
```env
# AI APIs
OPENAI_API_KEY=your_openai_key
COHERE_API_KEY=your_cohere_key
ANTHROPIC_API_KEY=your_anthropic_key
HUGGINGFACE_TOKEN=your_huggingface_token

# Image APIs
UNSPLASH_API_KEY=your_unsplash_key
PIXABAY_API_KEY=your_pixabay_key
PEXELS_API_KEY=your_pexels_key

# WordPress
WORDPRESS_URL=https://yourdomain.com
WORDPRESS_USER=your_user
WORDPRESS_APP_PASSWORD=your_app_password

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## 🧪 Testing

### Windows Compatibility Test
```bash
python test_windows.py
```

### System Test
```bash
python test_system.py
```

### App Test
```bash
python test_app.py
```

## 🚀 Deployment

### Windows
```cmd
# Install
install_windows.bat

# Run
python run.py
```

### Linux/Mac
```bash
# Install
pip install -r requirements.txt

# Run
python run.py
```

### Docker (Optional)
```bash
docker-compose up -d
```

## 📊 Performance

- **Keyword Processing**: 50 keywords per batch
- **Content Generation**: 1500 words per article
- **Image Generation**: 3 images per article
- **API Rate Limiting**: 60 requests per minute

## 🔒 Security

- Input validation
- XSS protection
- Rate limiting
- API key management
- Secure file handling

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
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
   ```bash
   mkdir output
   mkdir output/images
   mkdir templates
   mkdir static
   ```

### Testing Individual Components

Test imports:
```bash
python -c "import fastapi, uvicorn, pandas, requests, aiohttp; print('All imports successful')"
```

Test configuration:
```bash
python -c "from src.utils.config import Settings; s = Settings(); print('Configuration loaded')"
```

## 📚 Documentation

- **WINDOWS_README.md** - Windows-specific guide
- **QUICKSTART.md** - Quick start guide
- **DEVELOPMENT.md** - Development guide
- **SECURITY.md** - Security guide
- **PERFORMANCE.md** - Performance guide

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter issues:
1. Run `python test_windows.py` to check compatibility
2. Check the error messages
3. Verify your API keys
4. Ensure all directories exist

---

**Happy Content Generating! 🚀**

