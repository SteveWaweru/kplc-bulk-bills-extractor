import csv
import os
from cStringIO import StringIO

from flask import Flask, request, render_template, stream_with_context
import textract
import shutil

from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = 'uploads'
# ALLOWED_EXTENSIONS = set(['pdf'])
uploads_dir = app.config['UPLOAD_FOLDER']


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    if request.method == 'POST':
        def generate():
            data = StringIO()
            writer = csv.writer(data)
            writer.writerow(('Account', 'Amount'))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)
            f = request.files.getlist('filesToUpload')
            for bill in f:
                account = bill.filename.split('.')[0][5:]
                bill.save(os.path.join(uploads_dir, bill.filename))
                content = textract.process(os.path.join(uploads_dir, bill.filename), method='pdfminer')
                # TODO: Using Regex to extract the data
                amount = content.split('\n')[0][4:]
                # data.append([account, c2[5:]])
                writer.writerow((account, amount))
                yield data.getvalue()
                data.seek(0)
                data.truncate(0)
                print account, amount
            shutil.rmtree(uploads_dir)
        # stream the response as the data is generated
        response = Response(stream_with_context(generate()), mimetype='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=Bills.csv; charset=utf-16'
        return response
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0')