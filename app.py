from flask import Flask, render_template_string, request, send_file
import os
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
import img2pdf

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# HTML and CSS in one file
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Toolkit</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(45deg, #6a11cb, #2575fc);
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }
        h1 {
            text-align: center;
        }
        form {
            margin-bottom: 20px;
        }
        input[type="file"] {
            margin-bottom: 10px;
        }
        button {
            background-color: #2575fc;
            color: white;
            border: none;
            padding: 10px;
            cursor: pointer;
            border-radius: 5px;
        }
        button:hover {
            background-color: #6a11cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>PDF Toolkit</h1>

        <h3>Merge PDFs</h3>
        <form action="/merge" method="post" enctype="multipart/form-data">
            <input type="file" name="pdf_files" multiple>
            <button type="submit">Merge PDFs</button>
        </form>

        <h3>Split PDF</h3>
        <form action="/split" method="post" enctype="multipart/form-data">
            <input type="file" name="pdf_file">
            <button type="submit">Split PDF</button>
        </form>

        <h3>PDF to JPG</h3>
        <form action="/pdf_to_jpg" method="post" enctype="multipart/form-data">
            <input type="file" name="pdf_file">
            <button type="submit">Convert to JPG</button>
        </form>

        <h3>JPG to PDF</h3>
        <form action="/jpg_to_pdf" method="post" enctype="multipart/form-data">
            <input type="file" name="jpg_files" multiple>
            <button type="submit">Convert to PDF</button>
        </form>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# PDF Merge operation
@app.route('/merge', methods=['POST'])
def merge_pdf():
    files = request.files.getlist('pdf_files')
    merger = PdfFileMerger()

    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        merger.append(PdfFileReader(filepath, 'rb'))

    output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'merged.pdf')
    with open(output_path, 'wb') as output_file:
        merger.write(output_file)

    return send_file(output_path, as_attachment=True)

# PDF Split operation
@app.route('/split', methods=['POST'])
def split_pdf():
    file = request.files['pdf_file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    input_pdf = PdfFileReader(filepath)
    output_files = []
    
    for page in range(input_pdf.numPages):
        output = PdfFileWriter()
        output.addPage(input_pdf.getPage(page))

        output_filename = f'page_{page+1}.pdf'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        with open(output_path, 'wb') as output_pdf:
            output.write(output_pdf)
        output_files.append(output_filename)

    return f"PDF split successfully into {input_pdf.numPages} pages!"

# PDF to JPG operation
@app.route('/pdf_to_jpg', methods=['POST'])
def pdf_to_jpg():
    file = request.files['pdf_file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    images = convert_from_path(filepath)
    output_files = []
    
    for i, image in enumerate(images):
        output_filename = f'page_{i+1}.jpg'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        image.save(output_path, 'JPEG')
        output_files.append(output_filename)
    
    return f"PDF converted to {len(output_files)} JPG images!"

# JPG to PDF operation
@app.route('/jpg_to_pdf', methods=['POST'])
def jpg_to_pdf():
    files = request.files.getlist('jpg_files')
    output_pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], 'output.pdf')
    
    with open(output_pdf_path, 'wb') as f:
        f.write(img2pdf.convert([file.stream for file in files]))

    return send_file(output_pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
