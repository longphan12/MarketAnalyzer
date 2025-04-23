from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from pdf_processor import PDFProcessor
from ai_analyzer import AIAnalyzer
import logging
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            static_folder='../frontend',
            template_folder='../frontend')
app.config.from_object(config['default'])
config['default'].init_app(app)

pdf_processor = PDFProcessor()
ai_analyzer = AIAnalyzer()

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/analyze', methods=['POST'])
def analyze_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        # Save the file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the PDF
        with open(filepath, 'rb') as pdf_file:
            import pdfplumber
            pdf = pdfplumber.open(pdf_file)
            
            # Extract data
            housing_activity = pdf_processor.extract_housing_activity(pdf)
            subdivisions = pdf_processor.extract_subdivisions(pdf)
            builder_benchmark = pdf_processor.extract_builder_benchmark(pdf)
            
            # Get region from query parameters
            region = pdf_processor._find_region_in_text(pdf)
            
            # Generate AI analysis
            ai_analysis = ai_analyzer.analyze_market_data(region, {
                'housing_activity': housing_activity,
                'subdivisions': subdivisions,
                'builder_benchmark': builder_benchmark
            })
            
            # Clean up
            os.remove(filepath)
            
            return jsonify({
                'housing_activity': housing_activity,
                'subdivisions': subdivisions,
                'builder_benchmark': builder_benchmark,
                'ai_analysis': ai_analysis
            })
            
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], port=5000) 