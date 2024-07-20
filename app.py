from flask import Flask, render_template

app = Flask(__name__)

# Register blueprints from other files
from imgtotext import imgtotext_bp
from pdftotext import pdftotext_bp
from video import video_bp

app.register_blueprint(imgtotext_bp)
app.register_blueprint(pdftotext_bp)
app.register_blueprint(video_bp)

# Home route
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/image')
def image():
    return render_template('imagetotext.html')

@app.route('/pdf')
def pdf():
    return render_template('pdftotext.html')

@app.route('/video')

def video():
    return render_template('video.html')

if __name__ == "__main__":
    app.run(debug=True)
