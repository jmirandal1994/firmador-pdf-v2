from flask import Flask, render_template, request, send_file
import fitz  # PyMuPDF
import os
import zipfile
from werkzeug.utils import secure_filename
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
SIGNATURE_PATH = 'static/signature.png'  # Ruta de la imagen de firma

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('pdfs')
    signed_pdfs = []

    for file in files:
        if file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            pdf_bytes = file.read()
            signed_pdf = insert_signature(pdf_bytes)
            signed_pdfs.append((f"signed_{filename}", signed_pdf))

    if len(signed_pdfs) == 1:
        filename, filedata = signed_pdfs[0]
        return send_file(filedata, as_attachment=True, download_name=filename, mimetype='application/pdf')

    # Si hay múltiples PDFs → generar archivo ZIP
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        for filename, filedata in signed_pdfs:
            zipf.writestr(filename, filedata.getvalue())

    zip_buffer.seek(0)

    # Nombre del ZIP con fecha
    fecha = datetime.now().strftime('%d-%m-%Y')
    zip_name = f"documentos_firmados_{fecha}.zip"

    return send_file(zip_buffer, as_attachment=True, download_name=zip_name, mimetype='application/zip')

def insert_signature(pdf_data):
    doc = fitz.open(stream=pdf_data, filetype="pdf")
    signature = fitz.Pixmap(SIGNATURE_PATH)

    sig_width = 110
    sig_height = 50

    for page in doc:
        x0 = 370
        y0 = 750  # ← Altura fina, entre 735 y 760
        sig_rect = fitz.Rect(x0, y0, x0 + sig_width, y0 + sig_height)
        page.insert_image(sig_rect, pixmap=signature, overlay=True)

    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return output
import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)






