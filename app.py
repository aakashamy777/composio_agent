from flask import Flask, send_file
import os

app = Flask(__name__)

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/<path:path>')
def serve_file(path):
    if os.path.exists(path) and os.path.isfile(path):
        return send_file(path)
    return "Not Found", 404

if __name__ == '__main__':
    app.run()
