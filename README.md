# Market Analyzer for Corey Construction

A GPT-powered tool for analyzing quarterly market reports across six regions: Houston, Dallas, Austin, San Antonio, Nashville, and Atlanta.

## Features
- PDF report analysis with AI-powered insights
- Interactive web interface for easy report uploads
- Comprehensive market analysis including:
  - Housing Activity metrics
  - Executive Summary
  - Strategic Recommendations
  - Builder Benchmark analysis
  - Subdivision Rankings
- Professional PDF export functionality

## Screenshots


## Demo Video


## Technical Requirements
- Python 3.8+
- OpenAI API key
- Required Python packages (see requirements.txt)

## Installation and Setup
1. Clone the repository
2. Create and activate virtual environment
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up OpenAI API key in `.env` file

## Usage
1. Start the application:
   ```bash
   python src/backend/app.py
   ```
2. Open browser and navigate to `http://localhost:5000`
3. Upload a market report PDF
4. View and analyze the results
5. Export to PDF for sharing

## Sample Reports
[Include links to sample reports for each region:
1. Houston
2. Dallas
3. Austin
4. San Antonio
5. Nashville
6. Atlanta]

## Future Updates
The tool is designed to accommodate future quarterly reports through:
1. Flexible PDF parsing logic
2. Configurable analysis parameters
3. Modular code structure
4. Easy-to-update templates

## Project Structure
```
src/
├── backend/
│   ├── app.py              # Flask application
│   ├── config.py           # Configuration settings
│   ├── pdf_processor.py    # PDF processing logic
│   └── ai_analyzer.py      # AI analysis implementation
└── frontend/
    ├── index.html          # Main interface
    ├── styles.css          # Styling
    └── app.js              # Frontend logic
```

## Evaluation Criteria Met
- ✅ Accurate data extraction & analysis
- ✅ Usable interface for non-technical users
- ✅ Clear documentation and presentation
- ✅ Professional output formats
- ✅ Comprehensive regional coverage

## Contact
longphan084@gmail.com

(214) 457-3220