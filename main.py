import os
import uuid
import subprocess
import logging
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'streams'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max upload size

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_hls(input_path, output_dir):
    """Convert video to HLS format using FFmpeg"""
    os.makedirs(output_dir, exist_ok=True)
    
    hls_playlist = os.path.join(output_dir, 'playlist.m3u8')
    
    # HLS conversion command
    hls_cmd = [
        'ffmpeg', '-i', input_path,
        '-profile:v', 'baseline',
        '-level', '3.0',
        '-start_number', '0',
        '-hls_time', '10',
        '-hls_list_size', '0',
        '-f', 'hls',
        hls_playlist
    ]
    
    try:
        subprocess.run(hls_cmd, check=True)
        logger.info(f"HLS conversion completed for {input_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"HLS conversion failed: {e}")
        return False

def convert_to_dash(input_path, output_dir):
    """Convert video to DASH format using FFmpeg"""
    os.makedirs(output_dir, exist_ok=True)
    
    dash_playlist = os.path.join(output_dir, 'manifest.mpd')
    
    # DASH conversion command
    dash_cmd = [
        'ffmpeg', '-i', input_path,
        '-map', '0:v', '-map', '0:a',
        '-c:v', 'libx264', '-x264-params', 'keyint=60:min-keyint=60:no-scenecut=1',
        '-b:v:0', '1500k',
        '-c:a', 'aac', '-b:a', '128k',
        '-bf', '1', '-keyint_min', '60',
        '-g', '60', '-sc_threshold', '0',
        '-f', 'dash',
        '-use_template', '1', '-use_timeline', '1',
        '-init_seg_name', 'init-$RepresentationID$.m4s',
        '-media_seg_name', 'chunk-$RepresentationID$-$Number%05d$.m4s',
        '-adaptation_sets', 'id=0,streams=v id=1,streams=a',
        dash_playlist
    ]
    
    try:
        subprocess.run(dash_cmd, check=True)
        logger.info(f"DASH conversion completed for {input_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"DASH conversion failed: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Generate a unique ID for this video
        video_id = str(uuid.uuid4())
        
        # Create directories for this video
        video_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], video_id)
        os.makedirs(video_upload_dir, exist_ok=True)
        
        stream_output_dir = os.path.join(app.config['OUTPUT_FOLDER'], video_id)
        os.makedirs(stream_output_dir, exist_ok=True)
        
        # Save the original file
        filename = secure_filename(file.filename)
        file_path = os.path.join(video_upload_dir, filename)
        file.save(file_path)
        
        logger.info(f"File uploaded: {file_path}")
        
        # Create directories for each format
        hls_output_dir = os.path.join(stream_output_dir, 'hls')
        dash_output_dir = os.path.join(stream_output_dir, 'dash')
        
        # Process video asynchronously
        def process_video():
            # Convert to HLS
            hls_result = convert_to_hls(file_path, hls_output_dir)
            
            # Convert to DASH
            dash_result = convert_to_dash(file_path, dash_output_dir)
            
            return hls_result and dash_result
        
        success = process_video()
        
        if success:
            return jsonify({
                'id': video_id,
                'status': 'success',
                'hls_url': f'/stream/{video_id}/hls/playlist.m3u8',
                'dash_url': f'/stream/{video_id}/dash/manifest.mpd',
                'player_url': f'/player/{video_id}'
            })
        else:
            return jsonify({'error': 'Conversion failed'}), 500
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/stream/<video_id>/<format_type>/<path:filename>')
def stream_file(video_id, format_type, filename):
    """Serve the video stream files"""
    directory = os.path.join(app.config['OUTPUT_FOLDER'], video_id, format_type)
    return send_from_directory(directory, filename)

@app.route('/player/<video_id>')
def player(video_id):
    """Render the video player page"""
    # Make sure we're explicitly passing video_id to the template
    hls_url = f'/stream/{video_id}/hls/playlist.m3u8'
    dash_url = f'/stream/{video_id}/dash/manifest.mpd'
    return render_template('player.html', video_id=video_id, hls_url=hls_url, dash_url=dash_url)

@app.route('/videos')
def video_list():
    """List all available videos"""
    videos = []
    
    # Get all subdirectories in the streams folder
    for video_id in os.listdir(app.config['OUTPUT_FOLDER']):
        video_dir = os.path.join(app.config['OUTPUT_FOLDER'], video_id)
        
        if os.path.isdir(video_dir):
            hls_path = os.path.join(video_dir, 'hls', 'playlist.m3u8')
            dash_path = os.path.join(video_dir, 'dash', 'manifest.mpd')
            
            if os.path.exists(hls_path) or os.path.exists(dash_path):
                videos.append({
                    'id': video_id,
                    'hls_url': f'/stream/{video_id}/hls/playlist.m3u8' if os.path.exists(hls_path) else None,
                    'dash_url': f'/stream/{video_id}/dash/manifest.mpd' if os.path.exists(dash_path) else None,
                    'player_url': f'/player/{video_id}'
                })
    
    return jsonify(videos)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
