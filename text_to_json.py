import google.generativeai as genai
import re
import json
import time
from dotenv import load_dotenv  
import os
from typing import Dict, Optional
from PIL import Image
# Load environment variables
load_dotenv()


# Configure the Gemini API
API_KEY = os.getenv('API_KEY')
genai.configure(api_key=API_KEY)

def process_text_with_image(extracted_text, image_path):
    """Process text with image context for more accurate extraction."""
    try:
        # Load the image
        image_part = Image.open(image_path)
        
        generation_config = {
            "temperature": 1,
            "top_p": 1.0,
            "top_k": 32,
            "max_output_tokens": 2048,
        }

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
        )

        prompt = """
            You are a JSON conversion assistant specialized in extracting structured data from academic assessment materials. Your task is to process text inputs containing student examination marks and convert them into a standardized JSON format.

            CORE FUNCTIONALITY:
            - Extract specific data points from provided text/image inputs
            - Convert the data into a precisely formatted JSON object
            - Maintain consistent validation rules
            - Handle missing or invalid data appropriately

            DATA EXTRACTION RULES:
            1. Roll Number:
            - Extract 12-digit student roll number
            - It is mentioned as "Roll No: A23456789012"
            - Format: String of exactly 12 digits
            - Default: "000000000000" if not found

            2. Question Marks:
            - Questions: Q1 through Q6
            - Parts: a, b, c, d for each question
            - Default: 0 for any missing/invalid marks

            OUTPUT FORMAT:
            ```json
            {
                "roll_number": string,  // 12 digits
                "questions": {
                    "Q1": {"a": number, "b": number, "c": number, "d": number},
                    "Q2": {"a": number, "b": number, "c": number, "d": number},
                    "Q3": {"a": number, "b": number, "c": number, "d": number},
                    "Q4": {"a": number, "b": number, "c": number, "d": number},
                    "Q5": {"a": number, "b": number, "c": number, "d": number},
                    "Q6": {"a": number, "b": number, "c": number, "d": number}
                },
                "total_marks": number
            }
            ```

            VALIDATION REQUIREMENTS:
            1. Roll number must be exactly 12 digits, starts with A2.......
            2. All fields are required - use defaults for missing data
            3. Question totals must equal sum of their parts
            4. Total marks must equal sum of all question totals
            5. Do not confuse between the marks of the questions and other details.

            RESPONSE BEHAVIOR:
            - Return ONLY the JSON object with no additional text
            - Maintain exact format specified above
            - Use default values for any missing/invalid data
            - Ensure all calculations are accurate
            - Do not include explanations or notes in the response
            - Understand the data properly before processing

            Note: Use both text and image inputs for complete context, but prioritize text data when discrepancies exist.
        """

        response = model.generate_content([prompt, extracted_text, image_part])

        response_text = response.text
        json_match = re.search(r"```json\n(.*?)\n```", response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
            print(json_str)  # Debug print
            return json.loads(json_str)
        
        # If no JSON block found, try to parse the entire response
        try:
            return json.loads(response_text)
        except:
            print("Could not parse JSON from response")
            return None

    except Exception as e:
        print(f"Error in text-image processing: {e}")
        return None
        
# class AnswerSheetParser:
#     def __init__(self):
#         self.valid_marks = {0, 5, 8}

#     def parse_text(self, text: str) -> Optional[Dict]:
#         """Parse extracted text into structured data."""
#         try:
#             # Extract roll number
#             roll_match = re.search(r'Roll No\s*:?\s*(\d{12})', text, re.IGNORECASE)
#             if not roll_match:
#                 print("No valid 12-digit roll number found")
#                 return None
#             roll_number = roll_match.group(1)
            
#             # Initialize questions data
#             questions = {
#                 f'Q{q}': {'a': 0, 'b': 0, 'c': 0, 'd': 0}
#                 for q in range(1, 7)
#             }
            
#             # Extract marks
#             # Look for patterns like "Q1a: 5" or "1a. 5" or "Box 1: 5 (Q1a)"
#             patterns = [
#                 r'Q(\d)([a-d])\s*:?\s*(\d+)',
#                 r'(\d)([a-d])\.\s*(\d+)',
#                 r'Box\s*\d+\s*:\s*(\d+)\s*\(Q(\d)([a-d])\)'
#             ]
            
#             marks_found = False
#             for pattern in patterns:
#                 matches = re.finditer(pattern, text)
#                 for match in matches:
#                     if pattern.startswith('Box'):
#                         mark = int(match.group(1))
#                         q_num = match.group(2)
#                         part = match.group(3)
#                     else:
#                         q_num = match.group(1)
#                         part = match.group(2)
#                         mark = int(match.group(3))
                    
#                     if mark in self.valid_marks:
#                         questions[f'Q{q_num}'][part] = mark
#                         marks_found = True
            
#             if not marks_found:
#                 print("No valid marks found")
#                 return None
            
#             # Calculate total
#             total_marks = sum(
#                 mark 
#                 for q_data in questions.values() 
#                 for mark in q_data.values()
#             )
            
#             return {
#                 'roll_number': roll_number,
#                 'questions': questions,
#                 'total_marks': total_marks
#             }
            
#         except Exception as e:
#             print(f"Error parsing text: {e}")
#             return None

#     def format_output(self, data: Optional[Dict]) -> str:
#         """Format the parsed data as JSON string."""
#         if not data:
#             return "No valid data to format"
#         return json.dumps(data, indent=2)

# def extract_data_to_json(text):
#     """Extract structured data from text and convert to JSON format."""
#     try:
#         # Initialize dictionary to store extracted data
#         data = {
#             'roll_no': None,
#             'marks': {
#                 'Q1': {'a': 0, 'b': 0, 'c': 0, 'd': 0},
#                 'Q2': {'a': 0, 'b': 0, 'c': 0, 'd': 0},
#                 'Q3': {'a': 0, 'b': 0, 'c': 0, 'd': 0},
#                 'Q4': {'a': 0, 'b': 0, 'c': 0, 'd': 0},
#                 'Q5': {'a': 0, 'b': 0, 'c': 0, 'd': 0},
#                 'Q6': {'a': 0, 'b': 0, 'c': 0, 'd': 0}
#             }
#         }

#         # Split text into lines
#         lines = text.strip().split('\n')

#         # Extract roll number
#         for line in lines:
#             if 'Roll No:' in line:
#                 data['roll_no'] = line.split(':')[1].strip()
#                 break

#         # Extract marks
#         current_question = None
#         for line in lines:
#             if line.startswith('Q') and ':' in line:
#                 # Get question number and marks
#                 q_parts = line.split(':')
#                 current_question = q_parts[0].strip()  # Q1, Q2, etc.
                
#                 # Get marks for this question
#                 marks = q_parts[1].strip().split()
#                 if len(marks) == 4:  # Ensure we have all 4 parts
#                     data['marks'][current_question] = {
#                         'a': int(marks[0]),
#                         'b': int(marks[1]),
#                         'c': int(marks[2]),
#                         'd': int(marks[3])
#                     }

#         return data

#     except Exception as e:
#         print(f"Error extracting data: {e}")
#         return None

# def format_json_output(data):
#     """Format the JSON data for better readability."""
#     try:
#         if not data:
#             return None

#         # Calculate total marks
#         total = sum(
#             mark 
#             for question in data['marks'].values() 
#             for mark in question.values()
#         )

#         formatted_data = {
#             'roll_no': data['roll_no'],
#             'marks_by_question': data['marks'],
#             'total_marks': total
#         }

#         return formatted_data

#     except Exception as e:
#         print(f"Error formatting JSON: {e}")
#         return None

# # Test function to verify extraction
# def test_extraction(text):
#     """Test the extraction with sample text"""
#     parser = AnswerSheetParser()
#     result = parser.parse_text(text)
#     if result:
#         print("\nExtracted Data:")
#         print(parser.format_output(result))
#     else:
#         print("Failed to extract data")

# # Example usage
# if __name__ == "__main__":
    # sample_text = """
    # Roll No: 123456789012
    # Marks Awarded:
    # Q1a: 5 Q1b: 0 Q1c: 8 Q1d: 5
    # Q2a: 5 Q2b: 8 Q2c: 0 Q2d: 5
    # Q3a: 8 Q3b: 5 Q3c: 5 Q3d: 0
    # """
    # test_extraction(sample_text) 