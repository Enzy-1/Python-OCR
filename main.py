import os
import sys
import numpy as np
from flask import Flask, request, jsonify
from pdf2image import convert_from_path
from PIL import Image, UnidentifiedImageError
import easyocr
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])

app = Flask(__name__)

# Saludo para comprobar funcionamiento
@app.route('/', methods=['GET'])
def home():
    return "¡Hola! La API está funcionando."

# Función: extraer texto desde imagen
def extract_text_from_image(reader, image_path):
    try:
        image = Image.open(image_path)
        results = reader.readtext(np.array(image), detail=0)
        return "\n".join(results)
    except UnidentifiedImageError:
        raise ValueError("El archivo no es una imagen válida.")
    except Exception as e:
        raise RuntimeError(f"Error al procesar imagen: {str(e)}")

# Función: extraer texto desde PDF
def extract_text_from_pdf(reader, pdf_path, dpi=300):
    try:
        pages = convert_from_path(pdf_path, dpi=dpi)
        texts = []
        for i, page in enumerate(pages, start=1):
            results = reader.readtext(np.array(page), detail=0)
            texts.append("\n".join(results))
        return "\n\n".join(texts)
    except Exception as e:
        raise RuntimeError(f"Error al procesar PDF: {str(e)}")

# POST: extraer texto desde archivo local (ya guardado)
@app.route('/escaner-local', methods=['POST'])
def extract_text_from_local_file():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({'error': 'No se proporcionó el nombre del archivo.'}), 400

    filename = secure_filename(data['filename'].lower())
    file_path = os.path.join("documentos", filename)

    if not os.path.exists(file_path):
        return jsonify({'error': f'El archivo "{filename}" no existe.'}), 404

    try:
        reader = easyocr.Reader(['en', 'es'])

        if filename.endswith(('.png', '.jpg', '.jpeg')):
            text = extract_text_from_image(reader, file_path)
        elif filename.endswith('.pdf'):
            text = extract_text_from_pdf(reader, file_path)
        else:
            return jsonify({'error': 'Tipo de archivo no soportado.'}), 400

        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# POST: extraer texto desde archivo subido (desde frontend)
@app.route('/escaner', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nombre de archivo vacío.'}), 400

    filename = secure_filename(file.filename.lower())
    file_path = os.path.join("temp", filename)

    os.makedirs("temp", exist_ok=True)
    file.save(file_path)

    try:
        reader = easyocr.Reader(['en', 'es'])

        if filename.endswith(('.png', '.jpg', '.jpeg')):
            text = extract_text_from_image(reader, file_path)
        elif filename.endswith('.pdf'):
            text = extract_text_from_pdf(reader, file_path)
        else:
            return jsonify({'error': 'Tipo de archivo no soportado.'}), 400

        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': f'Error al procesar archivo: {str(e)}'}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# Iniciar Flask
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
