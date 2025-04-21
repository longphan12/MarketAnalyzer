import pdfplumber
from typing import Dict, List, Any
import logging
import re

def qoq_change(prev, curr):
    return ((curr - prev) / prev) * 100

def print_table(table):
    for row in table:
        print(row)

class PDFProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_housing_activity(self, pdf) -> Dict[str, Dict[str, float]]:
        metrics = {
            "QTR_CLOS": {},
            "QTR_STARTS": {},
            "TOTAL_INV": {},
            "TOTAL_SUPPLY": {}
        }

        pattern = re.compile(r"^[1234]Q\d{2}\b")

        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split("\n")

            for line in lines:
                if pattern.match(line):
                    fields = re.split(r"\s+", line.strip())
                    quarter = fields[0]

                    if quarter in ["3Q24", "4Q24"]:
                        try:
                            metrics["QTR_CLOS"][quarter] = int(fields[1].replace(",", ""))
                            metrics["TOTAL_INV"][quarter] = int(fields[6].replace(",", ""))
                            metrics["TOTAL_SUPPLY"][quarter] = float(fields[7])
                            metrics["QTR_STARTS"][quarter] = int(fields[8].replace(",", ""))
                        except (IndexError, ValueError) as e:
                            print(f"Skipping line due to error: {e}\nLine: {line}")
            
        # Add QoQ Change
        for key in metrics:
            if "3Q24" in metrics[key] and "4Q24" in metrics[key]:
                metrics[key]["QOQ_CHANGE"] = round(qoq_change(
                    prev=metrics[key]["3Q24"],
                    curr=metrics[key]["4Q24"]
                ), 1)

        return metrics

    

if __name__ == "__main__":
    pdf_path = "../Q4 2024 - MarketSummaryReport_ATL (1)Q4.pdf"
    processor = PDFProcessor()
    with open(pdf_path, "rb") as pdf_file:
        pdf = pdfplumber.open(pdf_file)
        housing_activity = processor.extract_housing_activity(pdf)
        print(housing_activity)
