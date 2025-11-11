class PromptTemplates:
    
    @staticmethod
    def first_question_generation(
        cv_text: str,
        job_description: str,
        job_title: str,
        company_name: str
    ) -> str:
        return f"""You are an experienced interviewer starting an interview for {job_title} at {company_name}.

    CANDIDATE'S CV:
    {cv_text[:2000]}

    JOB DESCRIPTION:
    {job_description[:2000]}

    Your task: Generate ONE opening question to start the interview.

    This should be:
    - A warm, professional opener
    - Related to their most relevant experience for this role
    - Encouraging and conversational
    - Open-ended to let them share their background

    Return ONLY the question text. No JSON, no extra formatting, no prefixes.

    Generate the opening question now:"""

    @staticmethod
    def followup_question_generation(
        conversation_history: str,
        cv_text: str,
        job_description: str,
        question_count: int,
        max_questions: int = 8
    ) -> str:
        return f"""You are conducting a job interview. Based on the conversation so far, generate the NEXT question.

    CONVERSATION SO FAR:
    {conversation_history}

    CANDIDATE'S CV (for context):
    {cv_text[:1500]}

    JOB REQUIREMENTS (for context):
    {job_description[:1500]}

    PROGRESS: This will be question {question_count + 1} of {max_questions}

    Generate ONE follow-up question that:
    1. Builds naturally on their previous answer
    2. Explores a different aspect of their experience or the role
    3. Assesses skills mentioned in the job description
    4. Feels conversational and engaging

    Return ONLY the question text. No JSON, no formatting, no prefixes like "Question:".

    Generate the next question now:"""
    
    @staticmethod
    def feedback_generation(
        conversation_history: str,
        cv_text: str,
        job_description: str,
        job_title: str
    ) -> str:
        return f"""You are an expert interview analyst. 
        Analyze this job interview and provide comprehensive feedback.
        Your output MUST be a valid JSON object.

JOB TITLE: {job_title}

JOB REQUIREMENTS:
{job_description}

CANDIDATE'S CV:
{cv_text[:2000]}

INTERVIEW TRANSCRIPT:
{conversation_history}

Provide a thorough analysis covering:

1. OVERALL PERFORMANCE SCORE (1-10):
   - Consider: relevance of answers, communication clarity, technical depth, alignment with job requirements

2. STRENGTHS (3-5 specific points):
   - What did the candidate do well?
   - Which skills were demonstrated effectively?
   - Specific examples from their answers

3. AREAS FOR IMPROVEMENT (3-5 specific points):
   - What could be stronger?
   - Where did answers lack depth?
   - Skills that need more demonstration

4. CV IMPROVEMENT SUGGESTIONS:
   - How should they modify their CV for THIS specific role?
   - What experiences should be highlighted more?
   - What's missing that the job requires?
   - Specific wording or section suggestions

OUTPUT FORMAT:
Return ONLY a JSON object with this exact structure. Ensure all strings are properly escaped.
{{
  "score": <integer>,
  "strengths": "<string>",
  "weaknesses": "<string>",
  "cv_improvements": "<string>"
}}

Be constructive, specific, and actionable. Use bullet points (•) for lists.

Generate the feedback now:"""
    
    @staticmethod
    def format_conversation_history(messages: list[dict]) -> str:
        formatted = []
        
        for msg in messages:
            role = msg['role']
            content = msg['content']

            if role == 'assistant':
                formatted.append(f"Interviewer: {content}")
            elif role == 'user':
                formatted.append(f"Candidate: {content}")

        return "\n\n".join(formatted)