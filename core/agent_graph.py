from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import ChatPromptTemplate

# 1. Define the State (This stays global as a Type definition)
class AgentState(TypedDict):
    company_name: str
    job_title: str
    job_description: str
    resume_text: str
    research_data: str
    cover_letter: str

# 2. Builder Function (Lazy Initialization)
def init_agent_graph(api_key: str):
    """
    Initializes the Graph and LLM only when called with a valid API Key.
    """
    if not api_key:
        raise ValueError("Groq API Key is missing.")

    # Initialize Tools & Model LOCALLY inside the function
    search_tool = DuckDuckGoSearchRun()
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",  # Updated model
        temperature=0.7, 
        api_key=api_key
    )

    # --- NODE 1: THE RESEARCHER ---
    def research_node(state: AgentState):
        print(f"🕵️ Researching {state['company_name']}...")
        company = state['company_name']
        
        # Search Query
        query = f"recent news mission values work culture of {company}"
        try:
            # Run search
            results = search_tool.run(query)
        except Exception as e:
            results = f"Could not fetch live data. Reason: {str(e)}"
        
        return {"research_data": results}

    # --- NODE 2: THE WRITER ---
    def writing_node(state: AgentState):
        print(f"✍️ Drafting letter for {state['job_title']}...")
        
        prompt_template = ChatPromptTemplate.from_template(
            """
            You are an expert career coach. Write a highly personalized cover letter.
            
            CANDIDATE PROFILE:
            {resume_text}
            
            JOB DETAILS:
            Role: {job_title} at {company_name}
            Description: {job_description}
            
            COMPANY RESEARCH (Use this to tailor the intro):
            {research_data}
            
            INSTRUCTIONS:
            1. Start with a strong hook referencing the company's recent news or values found in the research.
            2. Connect the candidate's specific skills to the job description.
            3. Keep it professional, concise, and persuasive.
            4. Do NOT include placeholders like [Insert Name]. Use the data provided.
            """
        )
        
        # Chain connects prompt -> LLM
        chain = prompt_template | llm
        
        response = chain.invoke({
            "resume_text": state['resume_text'],
            "job_title": state['job_title'],
            "company_name": state['company_name'],
            "job_description": state['job_description'],
            "research_data": state['research_data']
        })
        
        return {"cover_letter": response.content}

    # 3. Build the Graph
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("researcher", research_node)
    workflow.add_node("writer", writing_node)

    # Define Edges
    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "writer")
    workflow.add_edge("writer", END)

    # Compile and return the app
    return workflow.compile()