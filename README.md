# Market Analyzer for Corey Construction

A GPT-powered tool for analyzing quarterly market reports across six regions: Houston, Dallas, Austin, San Antonio, Nashville, and Atlanta.

## Important Notice
Due to OpenAI API cost coverage, this application is currently running locally only. Upon project selection, it will be deployed as a web service.

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

![Dashboard Overview](/src/public/landing.png)
![Analysis Sample Result](/src/public/1.png)
![Analysis Sample Result](/src/public/2.png)
![Analysis Sample Result](/src/public/3.png)


## Demo Video
```https://drive.google.com/file/d/1PrJxR7F_MD6J9zdgNFE8eaEeImMG8kzv/view?usp=drive_link```


## Technical Requirements
- Python 3.8+
- OpenAI API key
- Required Python packages (see requirements.txt)

## Installation and Setup
1. Clone the repository
2. Create and activate virtual environment by running the commands below
   ```bash
   python -m venv venv # Both macOS, Linux, and Windows
   source venv/bin/activate  # On macOS/Linux
   # or
   .\venv\Scripts\activate  # On Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up OpenAI API key
   - Go to https://auth.openai.com/log-in. Create an account if haven't already done so.
   - Go to "Your profile" by clicking the profile icon.
   - Go to API keys, generate a new secret key with the associated project, and copy the key (make sure to store it because the key can only be viewed once, or you'll have to generate another one).
   - Obtain the project ID (under Organization).
   - Create a file called ".env" file in project's root folder
   - In .env:
      ```bash
      OPENAI_API_KEY=your_api_key
      OPENAI_PROJECT_ID=your_project_id
      ```
5. Run the project:
   ```bash
   python3 src/backend/app.py
   # or
   python src/backend.app.py
   ```
6. Open `http://localhost:5000/`

## Usage
1. Open browser and navigate to `http://localhost:5000`
2. Upload a market report PDF
3. View and analyze the results
4. Export to PDF for sharing

## Sample reports
- Can be viewed in REPORTS directory.

## Future Updates
The tool is designed to accommodate future quarterly reports through:
1. Flexible PDF parsing logic (will find the approriate recent two quarters)
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
- Accurate data extraction & analysis
- Usable interface for non-technical users
- Clear documentation and presentation
- Professional output formats
- Comprehensive regional coverage

## Contact
Email: longphan084@gmail.com