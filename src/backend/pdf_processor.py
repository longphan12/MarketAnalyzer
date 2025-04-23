import pdfplumber
from typing import Dict, List, Any
import logging
import re
from datetime import datetime

def qoq_change(prev, curr):
    return ((curr - prev) / prev) * 100

def print_table(table):
    for row in table:
        print(row)

class PDFProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_quarter = None
        self.next_quarter = None
        self.quarter_pattern = r"^[1234]Q\d{2}\b"

    def _find_region_in_text(self, pdf) -> str:
        text = pdf.pages[0].extract_text()
        lines = text.split("\n")
        area_line = lines[1]
        area_line = area_line.split("|")
        area = area_line[0].strip()
        return area

    def _find_quarters_in_text(self, text: str) -> List[str]:
        """Find all quarters in the text and return the two most recent ones"""
        quarters = []
        lines = text.split("\n")
        for line in lines:
            match = re.search(self.quarter_pattern, line)
            if match:
                quarter = match.group(0)
                if quarter not in quarters:
                    quarters.append(quarter)
        
        # Sort quarters chronologically
        def quarter_key(q):
            # Extract quarter number and year
            q_num = int(q[0])  # First character is quarter number
            year = int(q[2:])  # Last two characters are year
            # Convert to a comparable number (e.g., Q1 2024 = 20241, Q4 2023 = 20234)
            return year * 10 + q_num
        
        # Sort in descending order (most recent first)
        quarters.sort(key=quarter_key, reverse=True)
        return quarters[:2] if len(quarters) >= 2 else quarters

    def _extract_quarters(self, pdf) -> None:
        """Extract the two most recent quarters from the PDF"""
        page = pdf.pages[1]  # Assuming housing activity is on page 1
        text = page.extract_text()
        quarters = self._find_quarters_in_text(text)
        
        if len(quarters) >= 2:
            self.next_quarter = quarters[0]  # Most recent
            self.current_quarter = quarters[1]  # Second most recent
        elif len(quarters) == 1:
            self.current_quarter = quarters[0]
            self.next_quarter = None
        else:
            raise ValueError("No quarters found in the PDF")

    def extract_housing_activity(self, pdf) -> Dict[str, Dict[str, float]]:
        # First, extract the quarters from the PDF
        self._extract_quarters(pdf)
        
        metrics = {
            "QTR_CLOS": {},
            "QTR_STARTS": {},
            "TOTAL_INV": {},
            "TOTAL_SUPPLY": {}
        }

        pattern = re.compile(self.quarter_pattern)
        page = pdf.pages[1]
        text = page.extract_text()
        lines = text.split("\n")
        for line in lines:
            if pattern.search(line):
                fields = re.split(r"\s+", line.strip())
                quarter = fields[0]

                if quarter in [self.current_quarter, self.next_quarter]:
                    try:
                        metrics["QTR_CLOS"][quarter] = int(fields[1].replace(",", ""))
                        metrics["TOTAL_INV"][quarter] = int(fields[6].replace(",", ""))
                        metrics["TOTAL_SUPPLY"][quarter] = float(fields[7])
                        metrics["QTR_STARTS"][quarter] = int(fields[8].replace(",", ""))
                    except (IndexError, ValueError) as e:
                        print(f"Skipping line due to error: {e}\nLine: {line}")
            
        # Add QoQ Change
        for key in metrics:
            if self.current_quarter in metrics[key] and self.next_quarter in metrics[key]:
                metrics[key]["QOQ_CHANGE"] = round(qoq_change(
                    prev=metrics[key][self.current_quarter],
                    curr=metrics[key][self.next_quarter]
                ), 1)

        return metrics
    
    def extract_subdivisions(self, pdf) -> Dict[str, float]:
        page = None
        for a in pdf.pages:
            text = a.extract_text()
            if "Subdivision Ranking By Annual Starts" in text:
                page = a
        # page = pdf.pages[13]
        text = page.extract_text()
        lines = text.split('\n')
        # for line in lines:
        #     print(line)
        line_total_ann_closings = lines[4].split(" ")
        total_ann_closings = int(line_total_ann_closings[2].replace(",", ""))
        
        closings = []
        for line in lines:
            if re.match(r"^\d{1,2}\s", line):  # Starts with 1- or 2-digit rank
                # Find all numbers in the line
                nums = re.findall(r"\d{1,3}(?:,\d{3})*", line)
                if len(nums) >= 2:
                    try:
                        ann_closings = int(nums[-1].replace(",", ""))
                        closings.append(ann_closings)
                    except ValueError:
                        continue
        
        top_10_closings = sum(closings[:10])
        top_25_closings = sum(closings[:25])

        return {
            "Top10_Closings": top_10_closings,
            "Top25_Closings": top_25_closings,
            "Top10_Percentage": round(top_10_closings / total_ann_closings * 100, 1),
            "Top25_Percentage": round(top_25_closings / total_ann_closings * 100, 1),
            "Total_Closings_All_Subdivisions": total_ann_closings
        }
        # print(total_ann_closings)

    def extract_builder_benchmark(self, pdf) -> Dict[str, float]:
        # Ensure quarters are extracted
        if not self.current_quarter or not self.next_quarter:
            self._extract_quarters(pdf)
            
        page = None
        for a in pdf.pages:
            text = a.extract_text()
            if "Builder Benchmark: Observed Closings" in text:
                page = a
        text = page.extract_text()
        lines = text.split('\n')

        # Find the total annual closings (from the "All Builders Totals" line)
        total_ann_closings = 0
        for line in lines:
            if line.startswith("All Builders Totals"):
                nums = re.findall(r"\d{1,3}(?:,\d{3})*", line)
                if len(nums) >= 5:
                    total_ann_closings = int(nums[-2].replace(",", ""))  # 2nd to last is annual
                break

        builder_data = []

        for line in lines:
            if re.match(r"^\d{1,2}\s", line):  # starts with rank number
                numbers = re.findall(r"\d{1,3}(?:,\d{3})*|\d+\.\d+", line)
                if len(numbers) >= 5:
                    try:
                        # Extract only the last 5 numeric values BEFORE % share
                        c3, c4, ann = map(lambda x: int(float(x.replace(",", ""))), numbers[3:6])                        
                        qoq = round(((c4 - c3) / c3) * 100, 1) if c3 > 0 else None

                        # Extract builder name from line (everything between rank and 1Q24)
                        name_match = re.match(r"^\d+\s+(.*?)\s+\d{1,3}(?:,\d{3})*", line)
                        builder_name = name_match.group(1) if name_match else "Unknown"

                        builder_data.append({
                            "Builder": builder_name,
                            self.current_quarter: c3,
                            self.next_quarter: c4,
                            "Annual": ann,
                            "QoQ_Change": qoq
                        })
                    except Exception:
                        continue

        top_10_closings = sum(b["Annual"] for b in builder_data[:10])
        top_25_closings = sum(b["Annual"] for b in builder_data[:25])

        return {
            "Top10_Closings": top_10_closings,
            "Top25_Closings": top_25_closings,
            "Top10_Percentage": round(top_10_closings / total_ann_closings * 100, 1),
            "Top25_Percentage": round(top_25_closings / total_ann_closings * 100, 1),
            "Total_Annual_Closings": total_ann_closings,
            "Builder_Data": builder_data
        }
        
    

if __name__ == "__main__":
    pdf_path = "../Q4 2024 - MarketSummaryReport_DFW (1)Q4.pdf"
    processor = PDFProcessor()
    with open(pdf_path, "rb") as pdf_file:
        pdf = pdfplumber.open(pdf_file)
        housing_activity = processor.extract_housing_activity(pdf)
        subdivisions = processor.extract_subdivisions(pdf)
        builder_benchmark = processor.extract_builder_benchmark(pdf)
        print(processor._find_region_in_text(pdf))
        print(housing_activity)
        print(subdivisions)
        print(builder_benchmark)