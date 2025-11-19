from io import BytesIO
from xhtml2pdf import pisa

def create_resume_pdf(data: dict) -> bytes:
    """
    Converts a resume dictionary into a PDF file bytes using a HTML template.
    """
    
    # 1. Extract Data safely
    name = data.get('contact_info', {}).get('name', 'Candidate Name')
    email = data.get('contact_info', {}).get('email', '')
    phone = data.get('contact_info', {}).get('phone', '')
    summary = data.get('summary', '')
    skills = ", ".join(data.get('skills', []))
    experience = data.get('experience', []) # Expecting list of dicts or dict with list

    # Handle varied structure of 'experience' from LLM
    if isinstance(experience, dict):
        # normalize if LLM returned nested dict
        experience = experience.get('history', []) or experience.get('jobs', [])

    # 2. Create HTML Template (Simple & Clean)
    # You can customize the CSS below to change the look
    exp_html = ""
    if isinstance(experience, list):
        for job in experience:
            role = job.get('role') or job.get('title', 'Role')
            company = job.get('company', 'Company')
            # Handle bullet points (could be list or string)
            desc = job.get('description', [])
            if isinstance(desc, list):
                desc_html = "".join([f"<li>{item}</li>" for item in desc])
            else:
                desc_html = f"<li>{desc}</li>"
            
            exp_html += f"""
            <div class='job'>
                <div class='job-header'><strong>{role}</strong> | {company}</div>
                <ul>{desc_html}</ul>
            </div>
            """

    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Helvetica, sans-serif; color: #333; }}
            .header {{ text-align: center; margin-bottom: 20px; }}
            h1 {{ margin: 0; color: #2c3e50; }}
            .contact {{ font-size: 12px; color: #666; margin-bottom: 10px; }}
            .section {{ margin-top: 15px; margin-bottom: 10px; border-bottom: 2px solid #2c3e50; padding-bottom: 5px; }}
            .section-title {{ font-size: 14px; font-weight: bold; color: #2c3e50; text-transform: uppercase; }}
            .content {{ font-size: 12px; line-height: 1.4; }}
            .job {{ margin-bottom: 10px; }}
            .job-header {{ font-weight: bold; }}
            ul {{ margin-top: 5px; padding-left: 20px; }}
            li {{ margin-bottom: 2px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{name}</h1>
            <div class="contact">{email} | {phone}</div>
        </div>

        <div class="section"><div class="section-title">Professional Summary</div></div>
        <div class="content">{summary}</div>

        <div class="section"><div class="section-title">Technical Skills</div></div>
        <div class="content">{skills}</div>

        <div class="section"><div class="section-title">Experience</div></div>
        <div class="content">
            {exp_html}
        </div>
    </body>
    </html>
    """

    # 3. Convert to PDF
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
    
    if pisa_status.err:
        return b""
    
    return pdf_buffer.getvalue()