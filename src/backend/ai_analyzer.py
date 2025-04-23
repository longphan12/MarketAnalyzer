import os
from openai import OpenAI
from typing import Dict, Any
import logging
from dotenv import load_dotenv

load_dotenv()

class AIAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            project=os.getenv("OPENAI_PROJECT_ID")  # Needed for sk-proj keys
        )

        self.system_prompt = """You are an expert market analyst specializing in the roofing industry. 
        Your task is to analyze housing market data and provide insights and recommendations for a roofing company.
        Focus on identifying opportunities and risks for roofing operations based on the market data."""

    def analyze_market_data(self, region: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market data and generate insights"""
        try:
            # Format the data for GPT
            formatted_data = self._format_data_for_gpt(region, data)
            
            # Generate analysis
            analysis = self._generate_analysis(formatted_data)
            
            return {
                "housingActivity": {
                    "totalClosings": data["housing_activity"]["QTR_CLOS"][list(data["housing_activity"]["QTR_CLOS"].keys())[-1]],
                    "averagePrice": data["housing_activity"]["TOTAL_INV"][list(data["housing_activity"]["TOTAL_INV"].keys())[-1]],
                    "pricePerSqFt": data["housing_activity"]["TOTAL_SUPPLY"][list(data["housing_activity"]["TOTAL_SUPPLY"].keys())[-1]]
                },
                "executiveSummary": {
                    "overview": analysis["overview"],
                    "keyFindings": analysis["keyFindings"]
                },
                "recommendations": {
                    "opportunities": analysis["opportunities"],
                    "actions": analysis["actions"]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating AI analysis: {str(e)}")
            if "insufficient_quota" in str(e):
                return {
                    "error": "AI analysis is currently unavailable due to API quota limits. Please check your OpenAI account billing status."
                }
            return {
                "error": "Failed to generate analysis"
            }

    def _format_data_for_gpt(self, region: str, data: Dict[str, Any]) -> str:
        """Format the data into a clear prompt for GPT"""
        housing_activity = data.get("housing_activity", {})
        subdivisions = data.get("subdivisions", {})
        builders = data.get("builder_benchmark", {})
        
        formatted = f"""
        Region: {region}
        
        Housing Activity:
        {self._format_housing_activity(housing_activity)}
        
        Subdivision Analysis:
        {self._format_subdivision_data(subdivisions)}
        
        Builder Analysis:
        {self._format_builder_data(builders)}
        """
        
        return formatted

    def _format_housing_activity(self, data: Dict[str, Any]) -> str:
        """Format housing activity data"""
        formatted = []
        for metric, values in data.items():
            if metric != "QOQ_CHANGE":
                current = list(values.values())[-1]
                previous = list(values.values())[-2]
                change = values.get("QOQ_CHANGE", 0)
                formatted.append(f"{metric}: {current} (Previous: {previous}, Change: {change}%)")
        return "\n".join(formatted)

    def _format_subdivision_data(self, data: Dict[str, Any]) -> str:
        """Format subdivision data"""
        return f"""
        Top 10 Subdivisions: {data.get("Top10_Percentage", 0)}% of total closings
        Top 25 Subdivisions: {data.get("Top25_Percentage", 0)}% of total closings
        Total Closings: {data.get("Total_Closings_All_Subdivisions", 0)}
        """

    def _format_builder_data(self, data: Dict[str, Any]) -> str:
        """Format builder data"""
        builder_data = data.get("Builder_Data", [])
        top_builders = "\n".join([
            f"{b['Builder']}: {b['Annual']} annual closings (QoQ Change: {b.get('QoQ_Change', 0)}%)"
            for b in builder_data[:5]  # Top 5 builders
        ])
        
        return f"""
        Top 10 Builders: {data.get("Top10_Percentage", 0)}% of market
        Top 25 Builders: {data.get("Top25_Percentage", 0)}% of market
        Total Annual Closings: {data.get("Total_Annual_Closings", 0)}
        
        Top 5 Builders:
        {top_builders}
        """

    def _generate_analysis(self, formatted_data: str) -> Dict[str, Any]:
        """Generate comprehensive analysis using GPT"""
        prompt = f"""
        Based on the following market data, provide a comprehensive analysis:

        {formatted_data}

        Please provide:
        1. A brief overview of the market conditions
        2. 3-5 key findings about the market
        3. 3-5 specific market opportunities for roofing operations
        4. 3-5 strategic actions to capitalize on these opportunities

        Format your response as a JSON object with the following structure:
        {{
            "overview": "brief overview text",
            "keyFindings": ["finding 1", "finding 2", "finding 3"],
            "opportunities": ["opportunity 1", "opportunity 2", "opportunity 3"],
            "actions": ["action 1", "action 2", "action 3"]
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # Using standard GPT-4 model
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        # Parse the JSON response
        import json
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON response: {str(e)}")
            return {
                "overview": "Error generating analysis",
                "keyFindings": ["Analysis generation failed"],
                "opportunities": ["Please try again later"],
                "actions": ["Contact support if the issue persists"]
            }
