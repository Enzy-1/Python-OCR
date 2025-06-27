import os
import sys
import numpy as np
from flask import Flask, request, jsonify
from pdf2image import convert_from_path
from PIL import Image
import easyocr

app = Flask(__name__)

# Ruta GET para saludar y verificar que la API está funcionando
@app.route('/', methods=['GET'])
def home():
    return "¡Hola! La API está funcionando."

# Función para extraer texto de imagen
def extract_text_from_image(reader, image_path):
    image = Image.open(image_path)
    results = reader.readtext(np.array(image), detail=0)
    return "\n".join(results)

# Función para extraer texto de PDF
def extract_text_from_pdf(reader, pdf_path, dpi=300):
    pages = convert_from_path(pdf_path, dpi=dpi)
    texts = []
    for i, page in enumerate(pages, start=1):
        results = reader.readtext(np.array(page), detail=0)
        texts.append("\n".join(results))
    return "\n\n".join(texts)

@app.route('/escaner-local', methods=['POST'])
def extract_text_from_local_file():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({'error': 'Filename not provided'}), 400

    filename = data['filename'].lower()
    file_path = os.path.join("documentos", filename)  # carpeta donde guardas archivos

    if not os.path.exists(file_path):
        return jsonify({'error': f'File "{filename}" not found'}), 404

    reader = easyocr.Reader(['en', 'es'])

    if filename.endswith(('.png', '.jpg', '.jpeg')):
        text = extract_text_from_image(reader, file_path)
    elif filename.endswith('.pdf'):
        text = extract_text_from_pdf(reader, file_path)
    else:
        return jsonify({'error': 'Unsupported file type'}), 400

    return jsonify({'text': text})


# Ruta POST para extraer texto de imágenes o PDFs
@app.route('/escaner', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    filename = file.filename.lower()
    file_path = os.path.join("temp", filename)

    os.makedirs("temp", exist_ok=True)
    file.save(file_path)

    try:
        reader = easyocr.Reader(['en', 'es'])  # Ajusta los idiomas según sea necesario

        if filename.endswith(('.png', '.jpg', '.jpeg')):
            text = extract_text_from_image(reader, file_path)
        elif filename.endswith('.pdf'):
            text = extract_text_from_pdf(reader, file_path)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400

        return jsonify({'text': text})

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            
            

# Iniciar la aplicación Flask
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

