import cv2
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Configure Gemini API
API_KEY = os.getenv('API_KEY')
genai.configure(api_key=API_KEY)

def extract_text_from_image(image_path):
    """Extract text from image using Gemini API."""
    try:
        # Load the image
        image_part = Image.open(image_path)
        
        # Configure Gemini
        generation_config = {
            "temperature": 0,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }

        # Initialize model
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config
        )

        # Create prompt
        prompt = """

**Primary Function:**  
You are an advanced Image Analysis and Text Extraction Assistant. Your primary function is to perform detailed extraction of both printed and handwritten text from images, ensuring no detail is overlooked. **In addition, make sure to accurately extract questions numbered 1–6 along with their subquestions labeled (a, b, c, d) and correctly capture the marks awarded for each.**

---

### EXTRACTION CAPABILITIES:
1. **Text Types:**
   - Printed text (machine-generated)
   - Handwritten text
   - Numbers and special characters
   - Form fields and labels
   - Stamps and watermarks
   - Headers and footers

2. **Spatial Information:**
   - Location of text elements
   - Text alignment and orientation
   - Page layout and structure
   - Tables and grid formats
   - Margins and spacing

3. **Text Properties:**
   - Font styles and sizes
   - Text colors
   - Underlining, strikethroughs
   - Text emphasis (bold, italic)
   - Quality/clarity of writing

---

### EXTRACTION METHODOLOGY:
1. **Systematic Approach:**
   - Top-to-bottom scanning
   - Left-to-right reading
   - Section-by-section analysis
   - Table cell-by-cell examination

2. **Content Categories:**
   - Main body text
   - Form fields
   - Annotations
   - Signatures
   - Dates and timestamps
   - Reference numbers
   - Mathematical expressions

3. **Context Preservation:**
   - Document structure
   - Relationships between elements
   - Hierarchical organization
   - Cross-references
   - Form field labels and values

---

### OUTPUT REQUIREMENTS:
1. **Content Organization:**
   - Present extracted text in a clear, structured manner.
   - Maintain the original document's formatting.
   - Indicate any unclear, ambiguous, or partially visible text.
   - Preserve spatial relationships between elements.

2. **Format Specifications:**
   - Use clear paragraph breaks.
   - Maintain list and table structures.
   - Preserve text alignment and special formatting.
   - Ensure that the extracted table structure exactly mirrors the original layout.

3. **Quality Indicators:**
   - Mark uncertain readings.
   - Note areas with poor image quality.
   - Flag potential ambiguities.
   - Highlight inference-based readings.

4. **Question and Marks Extraction:**
   - **Ensure that questions numbered 1–6, including their subquestions labeled (a, b, c, d), are extracted accurately.**
   - **Correctly capture and associate the marks awarded with each question and subquestion.**

5. **Table Extraction and Comparison:**
   - **Extract the table structure exactly as it appears, including header rows, subquestion rows, and rows for "CO Number" and "Marks Awarded".**
   - **Compare the extracted table with the original layout to ensure correct alignment of all columns and rows.**
   - **Confirm that the table concludes precisely with the row containing the marks awarded.**

6. **Total Marks Verification:**
   - **Calculate the sum of the individual marks extracted for each question (and subquestion, if applicable).**
   - **Verify that the calculated sum matches the provided total.**
   - **If there is a discrepancy (for example, if the extracted details indicate a total of 30 while another part of the table shows a different value), clearly flag this inconsistency.**
   - **In the provided example, the student's verification note states "marks are not matching with the total, that should be 30" – ensure that such comments and the corrected total (30) are highlighted.**

---

### SPECIAL CONSIDERATIONS:
1. **Image Quality:**
   - Account for blur, shadows, or glare.
   - Handle poor contrast or lighting.
   - Process faded or damaged text.
   - Manage overlapping or skewed/rotated elements.

2. **Text Complexity:**
   - Process mixed text types, including handwritten and printed text.
   - Handle multiple languages and varied writing styles.
   - Account for any corrections or edits within the document.

3. **Document Elements:**
   - Extract tables, grids, and form fields accurately.
   - Capture margins, headers/footers, and page numbers.
   - Preserve document metadata and structural elements.

---

### OUTPUT ORGANIZATION:
1. Start with the document type/purpose.
2. List main structural elements.
3. Detail content section by section.
4. Note any special elements, markings, or verification comments (e.g., "Student sign after marks verification").
5. Include relevant metadata.
6. Highlight key information, such as discrepancies in marks.
7. Maintain original formatting.
8. **For tables:**  
   - Ensure that the extracted table structure is compared with the original layout.
   - Verify that the table ends exactly with the row containing the marks awarded.
   - Confirm that the total marks match the sum of individual marks, and if not, flag the discrepancy (as in the example where the correct total should be 30).

---

### QUALITY ASSURANCE:
- Double-check numerical values and totals.
- Verify proper nouns and names.
- Cross-reference related elements.
- Ensure complete coverage of all document sections.
- Mark any uncertainties or discrepancies clearly.
- **Confirm that the total marks match the sum of individual marks and flag any mismatches.**

---


        """

        
        
        # Generate response
        response = model.generate_content([image_part, prompt])
        
        if response and response.text:
            print(f"Raw Gemini Response:\n{response.text}")  # Debug print
            return response.text
            
        return None

    except Exception as e:
        print(f"Error in text extraction: {e}")
        return None

# def get_valid_mark(mark):
#     """Convert mark to nearest valid value (0, 5, or 8)."""
#     try:
#         mark = int(mark)
#         if mark in [0, 5, 8]:
#             return mark
#         elif mark < 3:
#             return 0
#         elif mark < 6.5:
#             return 5
#         else:
#             return 8
#     except (ValueError, TypeError):
#         return 0

# def extract_data_to_json(text):
    """Convert extracted text to JSON format."""
    try:
        if not text:
            return None

        # Initialize data structure
        data = {
            'roll_number': '000000000000',
            'questions': {
                f'Q{i}': {'a': 0, 'b': 0, 'c': 0, 'd': 0}
                for i in range(1, 7)
            },
            'total_marks': 0
        }

        # Process text line by line
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Extract roll number
            if line.startswith('Roll No:'):
                roll_no = ''.join(filter(str.isdigit, line))
                if len(roll_no) >= 12:
                    data['roll_number'] = roll_no[:12]

            # Extract marks
            elif line.startswith('Q'):
                try:
                    q_num = line[1]
                    if not q_num.isdigit() or int(q_num) < 1 or int(q_num) > 6:
                        continue

                    # Extract marks without brackets
                    marks = line.split(':')[1].strip().split()
                    if len(marks) == 4:
                        q_key = f'Q{q_num}'
                        data['questions'][q_key] = {
                            'a': get_valid_mark(marks[0]),
                            'b': get_valid_mark(marks[1]),
                            'c': get_valid_mark(marks[2]),
                            'd': get_valid_mark(marks[3])
                        }
                except (IndexError, ValueError) as e:
                    print(f"Error parsing line '{line}': {e}")
                    continue

        # Calculate total marks
        total = sum(
            mark
            for q_data in data['questions'].values()
            for mark in q_data.values()
        )
        data['total_marks'] = total

        print(f"Processed JSON Data:\n{data}")  # Debug print
        return data

    except Exception as e:
        print(f"Error converting to JSON: {e}")
        return None 