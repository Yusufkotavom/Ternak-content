# 🚀 Quick Start Guide - Auto Content Generator

## Prerequisites

- Python 3.11+
- Git
- OpenAI API Key (optional, for AI content generation)
- Image API Keys (optional, for stock photos)

## Quick Installation

### 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/yourusername/auto-content-eeat.git
cd auto-content-eeat

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
nano .env
```

Add your API keys to `.env`:
```env
OPENAI_API_KEY=your_openai_key_here
UNSPLASH_API_KEY=your_unsplash_key_here
PIXABAY_API_KEY=your_pixabay_key_here
PEXELS_API_KEY=your_pexels_key_here
```

### 3. Run the Application

```bash
# Start the web interface
python run.py

# Or use the main file directly
python main.py
```

Open your browser: http://localhost:8000

## Quick Usage

### Web Interface

1. Go to http://localhost:8000
2. Upload CSV file or enter keywords manually
3. Click "Generate Content"
4. Download generated articles

### Command Line

```bash
# Single keyword
python cli.py --keyword "diet sehat"

# Multiple keywords
python cli.py --keywords "diet sehat" "tips menurunkan berat badan"

# CSV file
python cli.py --csv sample_keywords.csv

# Publish to WordPress
python cli.py --csv sample_keywords.csv --wordpress
```

### API Usage

```bash
# Upload CSV
curl -X POST -F "file=@sample_keywords.csv" http://localhost:8000/upload-keywords

# Process keywords
curl -X POST -H "Content-Type: application/json" \
  -d '{"keywords": ["diet sehat", "tips menurunkan berat badan"]}' \
  http://localhost:8000/process-keywords
```

## Sample Data

Use the included `sample_keywords.csv` file to test the system:

```csv
keyword,description
diet sehat,Panduan diet sehat untuk pemula
tips menurunkan berat badan,Cara efektif menurunkan berat badan
makanan tinggi protein,Daftar makanan sumber protein terbaik
```

## Testing

```bash
# Run system tests
python test_system.py

# Check health
curl http://localhost:8000/health
```

## Production Deployment

### Docker (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t auto-content-generator .
docker run -p 8000:8000 auto-content-generator
```

### Systemd Service

```bash
# Copy service file
sudo cp auto-content-generator.service /etc/systemd/system/

# Enable and start
sudo systemctl enable auto-content-generator
sudo systemctl start auto-content-generator
```

### Nginx Reverse Proxy

```bash
# Copy nginx config
sudo cp nginx.conf /etc/nginx/sites-available/auto-content-generator
sudo ln -s /etc/nginx/sites-available/auto-content-generator /etc/nginx/sites-enabled/

# Test and restart
sudo nginx -t
sudo systemctl restart nginx
```

## Troubleshooting

### Common Issues

1. **OpenAI API Error**
   - Check your API key in `.env`
   - Ensure you have credits in your OpenAI account

2. **Image Generation Fails**
   - Check image API keys in `.env`
   - Some APIs have rate limits

3. **WordPress Connection Fails**
   - Verify WordPress URL and credentials
   - Check if WordPress REST API is enabled

4. **Port Already in Use**
   ```bash
   # Change port in .env
   PORT=8001
   ```

### Logs

```bash
# View application logs
tail -f /var/log/auto-content-generator/app.log

# View systemd logs
journalctl -u auto-content-generator -f

# View nginx logs
tail -f /var/log/nginx/access.log
```

## Next Steps

1. **Customize Prompts**: Edit E-E-A-T prompts in `src/modules/content_generator.py`
2. **Add More APIs**: Integrate additional image or content APIs
3. **Scale Up**: Use Docker Swarm or Kubernetes for production
4. **Monitor**: Set up Prometheus/Grafana monitoring
5. **Backup**: Configure automated backups

## Support

- 📚 Documentation: See `README.md`
- 🐛 Issues: GitHub Issues
- 💬 Community: GitHub Discussions
- 📧 Email: your@email.com

---

**Happy Content Generating! 🎉**