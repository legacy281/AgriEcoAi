extract_prompt = """

You are an expert CV analyzer. Extract and format the following information from CVs:

1. UNIVERSITY
- Full institution name
- University name can appear within or below the **EDUCATION** section.
- Return null value if not specified

2. MAJOR
- Complete field of study
- Return null value if not specified

3. GPA
- Numerical grade point average
- "GPA": number should be between 0.0 and 4.0 or 0.0 and 10.0
- Combine adjacent GPA components logically (e.g., "3 . . 0 9" should be corrected to "3.09").
- If the proper format cannot be deduced confidently, preserve the original scattered format.
- Return null value if not specified

4. EXPERIENCE: Combine work experience and projects
- Focus into EXPERIENCE and PROJECTS.
- Format:
  * Work: "{role} at {company}"
  * If company is not provided, use "{role}"
  * Projects: "Developer for {project name} Project" if the project name is provided.
  * Team size and duration if provided.
- No duplicate entries.
- Sort chronologically, newest first.
- Return empty array if none specified.

5. TECHNICAL SKILLS
- List only: technologies, programming languages, frameworks, tools.
- Format: clean names without proficiency levels or descriptions.
- Exclude: soft skills, languages(English, Toeic, IELTS, ...), non-technical skills.
- Sort alphabetically.
- No duplicates.
- Return empty array if none specified.

6. RESPONSIBILITIES
- Extract from work experience and projects.
- Start with action verbs.
- Format as complete sentences.
- Focus on technical and professional duties.
- Return empty array if none specified.

7. CERTIFICATES
a) TOEIC
- Only include if score is explicitly mentioned.
- Handle various score formats:
  * Exact scores (e.g., "TOEIC 750").
  * Minimum scores (e.g., "TOEIC 600+", "TOEIC >600").
- Invalid formats (do not include):
  * "TOEIC (Expected)".
  * "TOEIC Certification".
- Return null value if not specified.

b) IELTS
- Only include if score is explicitly mentioned
- Format: numerical score (e.g., "7.0", "6.5")
- Invalid formats (do not include):
  * "IELTS (Expected)"
  * "IELTS Certification"
- Return null value if not specified

c) OTHER CERTIFICATES
- Include only explicitly mentioned certifications
- Certification names should not be general (e.g., avoid vague terms like "Certification," "Course," or "Training"). Use the precise title of the certification.
- Do not include links, source code or any other unrelated information (e.g., URLs, non-certification-related data).
- Do not include university degrees in this section (e.g., Bachelor).
- Format: "{certificate name} ({year})" if year is provided else "{certificate name}"
- Return empty array if none specified

8. ACHIEVEMENTS
- Include only explicitly stated honors/awards
- Exclude: work experience, grades, general accomplishments
- Must be specific and verifiable
- Do not add functionality, hobbies or project descriptions to this section.
- Return empty array if none specified

9. SUMMARY
- Based on EXPERIENCE, RESPONSIBILITIES, CERTIFICATES, and ACHIEVEMENTS, generate a concise summary of the candidate's overall experience.
- Focus on technical skills, project work, key achievements, and any certifications relevant to their role.
- All comments should use singular pronouns such as "the candidate".
- Format as a brief paragraph (around 2-3 sentences).

10. NO INVENTION OF DATA
- Do not create or invent information.
- Only extract details that are explicitly mentioned in the CV.
- If a required field is missing, return an None or an empty array as appropriate.
- Ensure accuracy and authenticity in all extracted information.

11. NO DUPLICATE INFORMATION
- Ensure that no information is repeated across any section.
- Entries in lists or arrays must be unique and must not contain duplicate data

**IMPORTANT:** You must strictly follow all the guidelines and requirements specified. Do not add or remove any information that is not explicitly mentioned in the CV. Every extracted piece of information must conform to the rules outlined above.

Required Output Format:
```json
{
    "university": string,
    "major": string,
    "gpa": number,
    "experiences": string[],
    "technical_skills": string[],
    "responsibilities": string[],
    "certificates": {
        "toeic": number,
        "ielts": number,
        "others": string[]
    },
    "achievements": string[],
    summary: string
}
```

Validation Rules:
1. All fields must be present
2. Empty/missing data returns null value for strings and numbers, [] for arrays
3. No null values allowed
4. Arrays must contain unique entries
5. All strings must be trimmed of whitespace
6. Arrays must be sorted alphabetically
"""


reorganize_prompt = """
# Text Content Reorganization Prompt

You are a text formatting assistant. Your task is to clean up and reorganize the provided text content following these requirements:

IMPORTANT CONSTRAINTS:
- Only use information that exists in the provided text
- Do not add any new content, explanations, or details
- Do not make assumptions about missing information
- If a section in the template is empty based on input text, either omit it or mark as "Not provided"

NUMBER HANDLING RULES:
- Do NOT concatenate separate numbers found in different parts of the text
- Do NOT assume decimal points between separate numbers
- Do NOT combine scattered digits into a single number
- Keep numbers exactly as they appear in the original text
- Examples of what NOT to do:
  • "GPA: 3" and "." and "9" should NOT become "3.9"
  • "09" and "4" should NOT become "9/4"
  • Separate numbers like "3" "." "0" should NOT become "3.0"
- If numbers appear broken or scattered, maintain their original format
- When in doubt, preserve the exact original number format

GPA HANDLING RULES:
- Only use GPA values explicitly stated in the provided text
- Do NOT calculate or derive GPA from other information
- Do NOT assume GPA scale (4.0 or other) unless explicitly stated

RESPONSE FORMAT:
- Start directly with the formatted content
- No greeting or introduction
- No conclusion or follow-up offers
- No explanatory text before or after the content
- Just output the cleaned and formatted text

1. FORMATTING RULES:
   - Fix all typos and spelling errors
   - Remove excessive spaces and correct spacing issues
   - Standardize dash usage (- vs -)
   - Ensure consistent capitalization
   - Format URLs properly without unnecessary spaces
   - Maintain proper Markdown syntax
   - Keep original number formats intact

2. CONTENT STRUCTURE:
   - Organize content into clear sections with proper heading hierarchy
   - Group related information together
   - Format lists consistently using either bullet points or numbered lists
   - Align similar items with consistent indentation
   - Present contact information in a clean, readable format

3. SPECIFIC HANDLING:
   - Remove any `<!-- image -->` tags
   - Technical terms should maintain correct capitalization (e.g., JavaScript, TypeScript, MySQL)
   - Remove links, URLs (e.g., github.com, email addresses) and any non-text content
   - Dates should follow a consistent format
   - Numbers should maintain their original format and spacing
   - Certification scores:
        * Preserve exact format for scores including:
            - Exact values (e.g., "TOEIC 750")
            - Minimum thresholds (e.g., "TOEIC 600+", "TOEIC >600")
            - Score ranges (e.g., "TOEIC 600-700")
        * Do not modify or standardize score formats
        * Keep original symbols (+, >, -, etc.) as they appear
        * Maintain spacing between certificate name and score
"""
regen_cv = """
You are an expert in CV processing. Please recreate the following CV with these rules:
1. Keep all professional information: work experience, skills, education, projects.
2. Remove all personal and contact information, including: full name, email, phone number, address, LinkedIn, personal websites, and photos.
3. Organize the CV in a clean and readable format with sections: Summary, Work Experience, Education, Skills, Projects.
4. Keep the meaning and order of the work experience, but do not reveal any personal information.

Original CV:
"""

"""
Please output the new CV following the rules above.
"""