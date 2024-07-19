from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.utils import secure_filename
import os
from videosum import process_video 
from ytvideosum import getYTsum

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['IMAGE_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['PDF_EXTENSIONS'] = {'pdf'}
app.config['VIDEO_EXTENSIONS'] = {'mp4'}
app.secret_key = 'your_secret_key'  # Needed for flashing messages

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/image', methods=['GET', 'POST'])
def image():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the image and get the summary
            summary = process_video(filepath)
            
            # Render the template with the summary
            return render_template('image.html', summary=summary)
    
    return render_template('image.html')

@app.route('/pdf')
def pdf():
    return render_template('pdf.html')

@app.route('/video')
def video():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename, app.config['VIDEO_EXTENSIONS']):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Process the uploaded video and get the summary
                summary = process_video(filepath)
                
                return render_template('video.html', summary=summary, video_type='uploaded')
            else:
                flash('Invalid file type. Allowed types are: ' + ', '.join(app.config['VIDEO_EXTENSIONS']))
                return redirect(request.url)
            
        elif 'youtube_url' in request.form:
            youtube_url = request.form['youtube_url']
            if youtube_url:
                try:
                    video_path = youtube_url
                    
                    # Process the YouTube video and get the summary
                    summary = getYTsum(video_path)
                    
                    return render_template('video.html', summary=summary)
                except Exception as e:
                    flash(f'Error processing YouTube video: {str(e)}')
                    return redirect(request.url)
            else:
                flash('No YouTube URL provided')
                return redirect(request.url)
        
        flash('Invalid request')
        return redirect(request.url)
    
    return render_template('video.html')

if __name__ == '__main__':
    app.run(debug=True)