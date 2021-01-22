import os
from flask import Flask, render_template, request, url_for, current_app
from werkzeug import secure_filename

app = Flask("nlp")

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
app.config['MEDIA_ROOT'] = os.path.join(PROJECT_ROOT, 'media_files')

@app.route("/", methods=['GET'])
def begin():
    return render_template('index.html', logo_url=url_for('static',filename='generic_logo.gif'))

@app.route("/", methods=['POST'])
def nsei():
    url_social_media = request.form['url']
    dados_do_formulario = request.form.to_dict()
    file_info = request.files.get('text')
    if file_info:
        filename = secure_filename(file_info.filename)
        path = os.path.join(current_app.config['MEDIA_ROOT'], filename)
        file_info.save(path)
        dados_do_formulario['text'] = filename
    return u"""<h1>Arquivo %s inserido com sucesso!</h1>
               <h1>Texto %s inserida com sucesso!</h1>
               <a href="%s"> Inserir nova notícia </a>
            """ % (filename, url_social_media, url_for('begin'))

@app.route("/<name>")
def index(name):
    if name.lower() == "bruno":
        return "Olá {}".format(name), 200
    else:
        return "Not Found", 404

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)