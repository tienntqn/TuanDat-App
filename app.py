from flask import Flask, request, send_file, render_template, jsonify, send_from_directory
import os, io
from processor import convert_excel

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

# Serve Zanex template assets from their original location
ZANEX_ASSETS = os.path.join(os.path.dirname(__file__), 'HTML', 'zanex', 'assets')

@app.route('/zanex/<path:filename>')
def zanex_static(filename):
    return send_from_directory(ZANEX_ASSETS, filename)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(ZANEX_ASSETS, 'images', 'brand'), 'favicon.ico')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')

@app.route('/sw.js')
def service_worker():
    resp = send_from_directory('static', 'sw.js', mimetype='application/javascript')
    resp.headers['Service-Worker-Allowed'] = '/'
    resp.headers['Cache-Control'] = 'no-cache'
    return resp


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400

    factory_name = request.form.get('factory_name', '').strip()
    if not factory_name:
        return jsonify({'error': 'Factory name is required'}), 400

    try:
        import os
        stem = os.path.splitext(file.filename)[0]
        download_name = f'{stem}-output.xlsx'
        input_bytes = file.read()
        output_bytes = convert_excel(input_bytes, factory_name)
        return send_file(
            io.BytesIO(output_bytes),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=download_name,
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 422
    except Exception as e:
        return jsonify({'error': f'Processing error: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
