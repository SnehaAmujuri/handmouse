from flask import Flask, render_template, jsonify
import os
import subprocess

app = Flask(__name__)

@app.route('/start-handmouse', methods=['GET'])
def start_handmouse():
    # Run the handmouse.py script
    script_path = os.path.join(os.path.dirname(__file__), 'handmouse.py')
    subprocess.Popen(['python3', script_path])
    return jsonify({"status": "Hand mouse script started"})

@app.route('/home', methods=['GET'])
def home():
    # Render the index.html file
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
