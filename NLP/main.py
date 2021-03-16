import os
import re
from werkzeug import secure_filename
from flask import Flask, render_template, request, url_for, current_app
from services.nlp import run
from services.scraping import read_file, yt_scrap, insta_scrap

app = Flask("nlp")

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
app.config['MEDIA_ROOT'] = os.path.join(PROJECT_ROOT, 'media_files')

@app.route("/", methods=['GET'])
def begin():
    return render_template('first.html', logo_url='/static/img/logo.png')


@app.route("/youtube", methods=['GET'])
def youtube():
    return render_template('scraping.html', logo_url='/static/img/logo.png', action='/youtube', first_input='Enter YouTube link: ', obs='* Interation is the number of times the page will scroll down to load new comments (each interation give 20 comments).')

@app.route("/youtube", methods=['POST'])
def show_yt():
    n = request.form['number']
    url = request.form['url']

    if not n.isdigit():
        return render_template('error.html', logo_url='/static/img/logo.png',err=f'The number {n} is WRONG!!!', 
                                err_description=f'Please select a positive integer and try again.', 
                                go_back=url_for('youtube'))
    else:
        n = int(n) + 1
        
    if not re.search('^https://www.youtube.com/|^http://www.youtube.com/|^www.youtube.com/|^youtube.com/', url):
        return render_template('error.html', logo_url='/static/img/logo.png',err=f'The URL {url} is WRONG!!!', 
                                err_description='It should follow the following format: https://www.youtube.com/watch?v=goMp OR http://www.youtube.com/watch?v=goMp OR www.youtube.com/watch?v=goMp OR youtube.com/watch?v=goMp.', 
                                go_back=url_for('youtube'))
    if re.search('^www.youtube.com/', url):
        url = 'https://' + url
    if re.search('^youtube.com/', url):
        url = 'https://www.' + url

    #lista = yt_scrap(url,n)
    #lista = run(lista)
    return render_template('graphics.html', logo_url='/static/img/logo.png')


@app.route("/insta", methods=['GET'])
def insta():
    return render_template('scraping.html', logo_url='/static/img/logo.png', action='/insta', first_input='Enter Instagram Post link: ', obs='* Interation is the number of times the button + will be click to load new comments.')

@app.route("/insta", methods=['POST'])
def show_insta():
    n = request.form['number']
    url = request.form['url']

    if not n.isdigit():
        return render_template('error.html', logo_url='/static/img/logo.png',err=f'The number {n} is WRONG!!!', 
                                err_description=f'Please select a positive integer and try again.', 
                                go_back=url_for('insta'))
    else:
        n = int(n)

    if not re.search('^https://www.instagram.com/|^http://www.instagram.com/|^www.instagram.com/|^instagram.com/', url):
        return render_template('error.html', logo_url='/static/img/logo.png',err=f'The URL {url} is WRONG!!!', 
                                err_description='It should follow the following format: https://www.instagram.com/p/B9POVGJ2Vy/ OR http://www.instagram.com/p/B9POVGJ2Vy/ OR www.instagram.com/p/B9POVGJ2Vy/ OR instagram.com/p/B9POVGJ2Vy/.', 
                                go_back=url_for('insta'))
    if re.search('^www.instagram.com/', url):
        url = 'https://' + url
    if re.search('^instagram.com/', url):
        url = 'https://www.' + url

    #lista = insta_scrap(url, n)
    #lista = run(lista)
    return render_template('graphics.html', logo_url='/static/img/logo.png')


@app.route("/upload", methods=['GET'])
def upload():
    return render_template('upload.html', logo_url='/static/img/logo.png')

@app.route("/upload", methods=['POST'])
def show_upload():
    file_info = request.files.get('text')
    if file_info:
        filename = secure_filename(file_info.filename)
        if filename[-4:] != '.txt':
            return render_template('error.html', logo_url='/static/img/logo.png',err=f'The extension {filename[-4:]} is WRONG!!!', 
                                   err_description='Please double check the file extension. We only accept files with extension .txt',
                                   go_back=url_for('upload'))
        path = os.path.join(current_app.config['MEDIA_ROOT'], filename)
        file_info.save(path)
    else:
        return render_template('error.html', logo_url='/static/img/logo.png',err=f'File {filename[:-4]} was not found!!!', 
                                err_description='Please check the file again and try again.', go_back=url_for('upload'))
    file_path = current_app.config['MEDIA_ROOT']+'/'+filename
    #lista = read_file(file_path)
    #lista = run(lista)
    return render_template('graphics.html', logo_url='/static/img/logo.png')


@app.route("/default", methods=['GET'])
def default():
    file_path = current_app.config['MEDIA_ROOT']+'/default.txt'
    #lista = read_file(file_path)
    #lista = run(lista)
    return render_template('graphics.html', logo_url='/static/img/logo.png')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)