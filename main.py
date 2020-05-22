from flask import Flask, render_template, request, send_from_directory
import math

import model

from transformers import pipeline

text_generator = pipeline("text-generation")


app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template('sign-up.html')

@app.route('/login')
def login():
    return render_template('log-in.html')

@app.route('/demo', methods=['POST', 'GET'])
def demo():
    # if request.method == 'GET':
    #     return render_template('demo.html')
    # else:
        input_text = "This is a"
        x = text_generator(input_text, max_length=800)
        #print(x)
        return render_template('demo.html', text=x)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 