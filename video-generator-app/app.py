import os
import subprocess
from flask import Flask, render_template, request, send_file, url_for
import tempfile

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_video', methods=['POST'])
def generate_video():
    if 'image' not in request.files or 'audio' not in request.files:
        return "Image or audio not provided", 400

    image_file = request.files['image']
    audio_file = request.files['audio']

    # টেম্পোরারি ফাইল তৈরি করা
    temp_dir = tempfile.gettempdir()
    image_path = os.path.join(temp_dir, image_file.filename)
    audio_path = os.path.join(temp_dir, audio_file.filename)
    output_path = os.path.join(temp_dir, 'output.mp4')
    
    image_file.save(image_path)
    audio_file.save(audio_path)

    # তোমার এফেক্ট ভিডিওর পাথ
    mist_effect_path = os.path.join(app.static_folder, 'effects', 'mist.mp4')
    soundwave_effect_path = os.path.join(app.static_folder, 'effects', 'soundwave.mp4')

    # FFmpeg কমান্ডে একাধিক ইনপুট যোগ করা
    # এখানে তুমি তোমার প্রয়োজন অনুযায়ী এফেক্ট যোগ করতে পারবে
    ffmpeg_command = [
        'ffmpeg',
        '-i', audio_path,           # ইনপুট 0: অডিও
        '-loop', '1',               
        '-i', image_path,           # ইনপুট 1: ইমেজ
        '-stream_loop', '-1',       
        '-i', mist_effect_path,     # ইনপুট 2: প্রথম এফেক্ট (C:\Users\RJ ONNU\Desktop\video_generator\Effect video\mist.mp4.mp4)
        '-stream_loop', '-1',
        '-i', soundwave_effect_path,# ইনপুট 3: দ্বিতীয় এফেক্ট (C:\Users\RJ ONNU\Desktop\video_generator\Effect video\soundwave.mp4.mp4)
        '-filter_complex',          
        '[1:v]scale=1280:720,setsar=1,fps=30[bg];' + # ইমেজকে ব্যাকগ্রাউন্ড হিসেবে সেট করা
        '[2:v]scale=1280:720,setsar=1,fps=30,format=yuva420p[mist];' +  # mist এফেক্টকে ফোরগ্রাউন্ডে সেট করা
        '[3:v]scale=1280:720,setsar=1,fps=30,format=yuva420p[soundwave];' +  # soundwave এফেক্টকে ফোরগ্রাউন্ডে সেট করা
        '[bg][mist]overlay=0:0:shortest=1[temp];' + # ব্যাকগ্রাউন্ড এবং প্রথম এফেক্ট ওভারলে করা
        '[temp][soundwave]overlay=0:0:shortest=1[v];' + # আগের আউটপুটের সাথে দ্বিতীয় এফেক্ট ওভারলে করা
        '[0:a]aresample=44100[a]',   # অডিওর স্যাম্পলিং রেট ঠিক করা
        '-map', '[v]',               
        '-map', '[a]',               
        '-shortest',                
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-pix_fmt', 'yuv420p',
        output_path
    ]

    try:
        subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        return send_file(output_path, as_attachment=True, download_name='generated_video.mp4')
    except subprocess.CalledProcessError as e:
        print("FFmpeg Error:", e.stderr)
        return f"Failed to generate video: {e.stderr}", 500
    finally:
        os.remove(image_path)
        os.remove(audio_path)
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == '__main__':
    app.run(debug=True)