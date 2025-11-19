import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

def tailor_resume(profile: dict, job_description: str, api_key: str) -> dict:
    """
    Uses LLM to rewrite resume summary and experience bullets to match a specific JD.
    """
    if not api_key:
        raise ValueError("API Key missing.")

    llm = ChatGroq(
    model_name="llama-3.3-70b-versatile", 
    temperature=0.5, 
    api_key=api_key
)

    # We want the LLM to return strict JSON
    parser = JsonOutputParser()

    prompt = ChatPromptTemplate.from_template(
        """
        You are an expert Resume Writer. Your goal is to tailor a candidate's resume to a specific Job Description.
        
        JOB DESCRIPTION:
        {job_description}
        
        CANDIDATE PROFILE (JSON):
        {profile_json}
        
        INSTRUCTIONS:
        1. Rewrite the "summary" to emphasize skills relevant to the JD.
        2. Rewrite the "experience" bullet points to highlight achievements that match the JD keywords.
        3. Keep the structure exactly the same as the input JSON (same keys).
        4. Do not invent fake experiences. Only rephrase existing ones.
        5. Return ONLY valid JSON.
        
        {format_instructions}
        """
    )

    chain = prompt | llm | parser

    # Convert profile dict to string for prompt
    profile_str = json.dumps(profile)

    try:
        tailored_json = chain.invoke({
            "job_description": job_description,
            "profile_json": profile_str,
            "format_instructions": parser.get_format_instructions()
        })
        return tailored_json
    except Exception as e:
        print(f"Tailoring Error: {e}")
        return profile # Return original if styling fails