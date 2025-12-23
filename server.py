from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import os
import uuid

app = Flask(__name__)

BASE_DIR = os.getcwd()
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

DEFAULT_RES = 720


@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "endpoints": {
            "mp3": "/download/mp3?url=YOUTUBE_URL",
            "mp4": "/download/mp4?url=YOUTUBE_URL&res=720"
        }
    })


@app.route("/download/mp3")
def download_mp3():
    url = request.args.get("url")
    if not url:
        return {"error": "url required"}, 400

    file_id = str(uuid.uuid4())
    output = os.path.join(DOWNLOAD_DIR, f"{file_id}.mp3")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output,
        "quiet": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return jsonify({
            "status": "success",
            "download_url": f"/file/{file_id}.mp3"
        })

    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/download/mp4")
def download_mp4():
    url = request.args.get("url")
    if not url:
        return {"error": "url required"}, 400

    try:
        res = int(request.args.get("res", DEFAULT_RES))
    except:
        res = DEFAULT_RES

    file_id = str(uuid.uuid4())
    output = os.path.join(DOWNLOAD_DIR, f"{file_id}.mp4")

    ydl_opts = {
        "format": f"bestvideo[ext=mp4][height<={res}]+bestaudio[ext=m4a]/best",
        "outtmpl": output,
        "merge_output_format": "mp4",
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return jsonify({
            "status": "success",
            "download_url": f"/file/{file_id}.mp4"
        })

    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/file/<path:filename>")
def serve_file(filename):
    return send_from_directory(
        DOWNLOAD_DIR,
        filename,
        as_attachment=True
      )
