from flask import Flask, request, send_file
from werkzeug.utils import secure_filename

from speech2Text.service import service

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'
@app.route('/uploadfile',methods=['GET','POST'])
def uploadfile():
    if request.method == 'POST':
        f = request.files['file']
        filePath = "./speech2Text/audio/"+secure_filename(f.filename)
        f.save(filePath)
        textConversionResult = request.values['destination-file-name']

        data,error = service.convert_to_text(filePath,textConversionResult)
        #response_file = 'speech2Text/savings/' + textConversionResult + ".txt"
        if data:
            return data
        else:
            return error


if __name__ == '__main__':
    app.run()
