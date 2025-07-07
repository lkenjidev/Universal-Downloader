from flask import Flask, render_template, request, send_file, after_this_request
import yt_dlp
import os
import uuid
import threading

app = Flask(__name__)

#roda o arquivo html
@app.route('/')
def index():
    return render_template('index.html')

#pega as informações do formulário HTML
@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    formato = request.form['formato']  
    qualidade = request.form['qualidade']  

    #cria um nome aleatorio pra fazer o download sem dar conflito com outro arquivo pré-existente
    saida_temporaria = f"{uuid.uuid4()}.%(ext)s"
    ydl_opts = {
        'outtmpl': saida_temporaria,
        'quiet': True
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
    else:
        if qualidade == 'alta':
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
            ydl_opts['merge_output_format'] = 'mp4'
        elif qualidade == 'media':
            ydl_opts['format'] = 'worstvideo+worstaudio/worst'
            ydl_opts['merge_output_format'] = 'mp4'
        elif qualidade == 'audio':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['merge_output_format'] = 'mp4'

    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            arquivo_final = ydl.prepare_filename(info)
            if formato == 'mp3':
                arquivo_final = os.path.splitext(arquivo_final)[0] + '.mp3'

            titulo = info.get('title', 'video')
            extensao = 'mp3' if formato == 'mp3' else 'mp4'
            nome_para_download = f"{titulo}.{extensao}"

    except Exception as e:
        return f"Erro ao baixar o vídeo: {e}"

    # remover arquivo após alguns segundos para evitar erro de permissão
    @after_this_request
    def remover_arquivo(response):
        def apagar():
            try:
                if os.path.exists(arquivo_final):
                    os.remove(arquivo_final)
            except Exception as e:
                print(f"Erro ao remover arquivo: {e}")

        threading.Timer(5, apagar).start()  
        return response

    return send_file(
        arquivo_final,
        as_attachment=True,
        download_name=nome_para_download,
        conditional=False
    )

#executa o programa
if __name__ == '__main__':
    app.run(debug=True)
