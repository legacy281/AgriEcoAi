extract_prompt = """

Analyze the job description (JD) step by step and extract information strictly based on the provided details. Do not use general knowledge or assumptions beyond what is explicitly mentioned in the JD.

### Extraction Guidelines:

1. **Position Title**:
    - Identify the job title or role mentioned in the JD.

2. **Responsibilities**:
    - Extract key responsibilities or tasks explicitly listed for the role.
    - Avoid rephrasing or inferring responsibilities that are not directly stated.

3. **Requirements**:
    - Experience: Extract professional experience requirements (e.g., years of experience).

4. **Technical Skills**:
    - List only: technologies, programming languages, frameworks, tools
    - Format: clean names without proficiency levels or descriptions
    - Exclude: soft skills, languages(English, Toeic, IELTS, ...), non-technical skills
    - Sort alphabetically
    - No duplicates

### Notes:
- Ensure the extracted information is concise, structured, and directly based on the JD.
- If any details are missing in the JD, leave the corresponding fields blank without making assumptions.

### Output Format:
{
    "position_title": position title,
    "responsibilities": [List of responsibilities],
    "requirements": {
        "education": ["List of educational qualifications required"],
        "technical_skills": [List of technical skills required],
        "experience": [List of professional experience requirements]
    },
}

Validation Rules:
1. All fields must be present
2. Empty/missing data returns None for strings, [] for arrays
3. No null values allowed
4. Arrays must contain unique entries
5. All strings must be trimmed of whitespace
6. Arrays must be sorted alphabetically
"""
