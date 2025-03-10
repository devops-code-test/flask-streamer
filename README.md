# Flask Video Streaming App

A modern video streaming application built with Flask and FFmpeg that supports adaptive streaming formats (HLS and DASH) for smooth playback across different network conditions.

## Features

- **File Upload**: Secure video file upload with drag-and-drop support
- **Adaptive Streaming**: Converts videos to HLS and DASH formats
- **Modern UI**: Responsive interface built with Tailwind CSS and Alpine.js
- **Video Player**: Built-in player supporting both HLS and DASH playback
- **File Management**: List and manage uploaded videos
- **Cross-Platform**: Works on desktop and mobile browsers

## Prerequisites

- Python 3.7+
- FFmpeg
- Modern web browser with HTML5 video support

## Setup Development Environment

1. Fork and Clone the repository:
```bash
git clone https://github.com/yourusername/flask-streamer.git
cd flask-streamer
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Install FFmpeg:
- **Ubuntu/Debian**:
  ```bash
  sudo apt update
  sudo apt install ffmpeg
  ```
- **macOS**:
  ```bash
  brew install ffmpeg
  ```
- **Windows**: Download from [FFmpeg official website](https://ffmpeg.org/download.html)

## Usage

1. Start the Flask server:
```bash
python main.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Upload a video file using the web interface:
   - Drag and drop a video file or click to browse
   - Wait for the conversion process to complete
   - Access your video through the player or direct streaming URLs

## Supported Video Formats

Input formats:
- MP4
- AVI
- MOV
- MKV
- WMV
- FLV
- WebM

Output formats:
- HLS (.m3u8)
- DASH (.mpd)

## Project Structure

```
flask-streamer/
├── main.py              # Main Flask application
├── requirements.txt     # Python dependencies
├── uploads/            # Original video storage
├── streams/            # Converted stream files
└── templates/          # HTML templates
    ├── index.html     # Main upload interface
    └── player.html    # Video player page
```

## Configuration

Default configurations in `main.py`:
- Maximum upload size: 100MB
- Server host: 0.0.0.0
- Server port: 5000
- Debug mode: Enabled

## Security Considerations

- File type validation
- Secure filename handling
- Size limitations
- Cross-Origin Resource Sharing (CORS) enabled

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [FFmpeg](https://ffmpeg.org/)
- [Video.js](https://videojs.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Alpine.js](https://alpinejs.dev/)
