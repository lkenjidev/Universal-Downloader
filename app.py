from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    formato = request.form['formato'] #mp4 ou mp3
    qualidade = request.form['qualidade']

    #gera um nome aleatorio e atribui ao video a ser salvo
    nome_arquivo = f"{uuid.uuid4()}.{formato}"
    ydl_opts = {
        'outtmpl': nome_arquivo,
    }

    if formato == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
        })
    else: #ou seja, mp4
        if qualidade == 'alta':
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
            ydl_opts['merge_output_format'] = 'mp4'
        elif qualidade == 'media':
            ydl_opts['format'] = 'worstvideo+worstaudio/worst'
            ydl_opts['merge_output_format'] = 'mp4'
        

    try: 
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return send_file(nome_arquivo, as_attachment=True)
    finally:
        if os.path.exists(nome_arquivo):
            os.remove(nome_arquivo)


