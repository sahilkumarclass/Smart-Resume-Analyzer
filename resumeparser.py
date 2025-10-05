import os, json
from openai import OpenAI

def load_api_key():
    """Load OpenAI API key from environment variable OPENAI_API_KEY."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY environment variable is not set")
    return api_key

def ats_extractor(resume_data, job_description=None):
    """
    Extract structured information from resume text using OpenAI API and optionally
    evaluate the resume against a job description to compute an ATS match score.

    Args:
        resume_data (str): Raw resume text content
        job_description (str | None): Optional job description text

    Returns:
        str: JSON formatted object containing extracted resume info, and if
             job_description is provided, an `ats` object with score and insights.
    """

    api_key = load_api_key()

    base_prompt = '''
    You are an AI assistant that parses resumes into structured JSON.
    Given ONLY the resume text, extract the following fields:
    - full_name
    - email
    - github
    - linkedin
    - employment: array of {company, position, location, start_date, end_date, responsibilities}
    - projects: array of {name, description, technologies, year}
    - technical_skills: object of categories to array of skills
    - soft_skills: array of strings

    Respond with STRICT JSON. No commentary.
    '''

    evaluation_prompt = '''
    In addition to parsing, if a Job Description (JD) is provided, evaluate how well the resume matches the JD.
    Produce an `ats` object with:
    - score: integer 0-100 representing match level
    - missing_keywords: array of top missing keywords from JD
    - strengths: array of short bullet insights on strong matches
    - recommendations: array of concrete, actionable improvements to increase ATS score

    Ensure final output is a single JSON object combining parsed resume fields and the `ats` object when JD is present.
    '''

    system_prompt = base_prompt + ("\n" + evaluation_prompt if job_description else "")

    openai_client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

    user_content = {
        "resume": resume_data.strip()
    }
    if job_description:
        user_content["job_description"] = job_description.strip()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(user_content)}
    ]

    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.0,
            max_tokens=2000
        )
        extracted_data = response.choices[0].message.content
        return extracted_data
    except Exception as e:
        raise Exception(f"Error during API call: {str(e)}")

if __name__ == "__main__":
    # Example usage
    sample_resume = """
    Your resume text goes here...
    """
    
    result = ats_extractor(sample_resume)
    print(result)