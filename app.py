from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import os
import subprocess
from pytube import YouTube
from dotenv import load_dotenv

# Configuración de la aplicación
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Cambia esta clave para producción

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Ruta para la carpeta de Descargas del usuario
DOWNLOAD_FOLDER = os.path.join(os.path.expanduser('~'), 'Downloads')
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Función para descargar video o audio
def download_video_or_audio(url, format_type):
    try:
        yt = YouTube(url)
        title = yt.title  # Obtener el título del video
        title = title.replace('/', '_').replace('\\', '_')  # Reemplazar caracteres que no son válidos en nombres de archivos

        if format_type == 'mp4':
            stream = yt.streams.get_highest_resolution()
            filename = f'{title}.mp4'
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            stream.download(output_path=DOWNLOAD_FOLDER, filename=filename)
        elif format_type == 'mp3':
            stream = yt.streams.filter(only_audio=True).first()
            filename = f'{title}.mp4'
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            stream.download(output_path=DOWNLOAD_FOLDER, filename=filename)
            output_file = os.path.join(DOWNLOAD_FOLDER, f'{title}.mp3')
            subprocess.run(['ffmpeg', '-i', file_path, output_file])
            os.remove(file_path)
            filename = f'{title}.mp3'
        elif format_type == 'avi':
            stream = yt.streams.get_highest_resolution()
            filename = f'{title}.mp4'
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            stream.download(output_path=DOWNLOAD_FOLDER, filename=filename)
            output_file = os.path.join(DOWNLOAD_FOLDER, f'{title}.avi')
            subprocess.run(['ffmpeg', '-i', file_path, output_file])
            os.remove(file_path)
            filename = f'{title}.avi'
        else:
            raise ValueError('Formato no soportado')

        return os.path.join(DOWNLOAD_FOLDER, filename)  # Devolver la ruta completa del archivo

    except Exception as e:
        raise e

# Ruta principal
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        format_type = request.form.get('format')

        if not url:
            flash('Por favor, ingrese una URL de YouTube.', 'error')
            return redirect(url_for('index'))

        try:
            file_path = download_video_or_audio(url, format_type)
            flash(f'Descarga completada con éxito. Haga clic en el enlace a continuación para descargar el archivo.', 'success')
            return redirect(url_for('download', filename=os.path.basename(file_path)))
        except Exception as e:
            flash(f'Error al descargar el video: {str(e)}', 'error')
        
    return render_template('index.html')

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash('El archivo no existe.', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

