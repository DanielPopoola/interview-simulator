class PromptTemplates:

    @staticmethod
    def interview_question_generation(
        cv_text: str,
        job_description: str,
        job_title: str,
        company_name: str
    ) -> str:
        return f"""You are an experienced technical interviewer conducting 
        an interview for the position of {job_title} at {company_name}.

CANDIDATE'S CV:
{cv_text[:2000]}

JOB DESCRIPTION:
{job_description[:2000]}

Your task: Generate 6-8 relevant interview questions for this candidate.

REQUIREMENTS:
1. Questions should be tailored to BOTH the candidate's background AND the job requirements
2. Mix different types:
   - Technical skills assessment
   - Experience-based questions
   - Behavioral questions
   - Questions about gaps or transitions in their CV
3. Questions should be appropriate for the seniority level
4. Be specific, not generic

OUTPUT FORMAT:
Return ONLY a JSON array of question strings. No other text.

Example format:
[
  "I see you worked with Python for 3 years. Can you walk me through a challenging technical 
  problem you solved using Python?",
  "The job requires experience with microservices -
  How have you designed or worked with microservices architectures?",
  "Tell me about a time when you had to learn a new technology quickly - 
  How did you approach it?"
]

Generate the questions now:"""
    
    @staticmethod
    def followup_question_generation(
        conversation_history: str,
        cv_text: str,
        job_description: str,
        question_count: int,
        max_questions: int = 8
    ) -> str:
        should_continue = question_count < max_questions
        
        if should_continue:
            instruction = """Based on the conversation so far, generate ONE follow-up question.

The question should:
1. Build on their previous answer
2. Dive deeper into relevant areas
3. Assess skills mentioned in the job description
4. Be natural and conversational

Return ONLY the question text. No JSON, no extra formatting."""
        else:
            instruction = """The interview has covered sufficient ground. Generate a polite closing statement.

Example: "Thank you for your detailed responses. 
That concludes our interview today. We'll be in touch soon regarding next steps."

Return ONLY the closing statement."""
        
        return f"""You are conducting a job interview for a candidate.

CONVERSATION SO FAR:
{conversation_history}

CANDIDATE'S CV (for context):
{cv_text[:1500]}

JOB REQUIREMENTS (for context):
{job_description[:1500]}

QUESTION COUNT: {question_count} of {max_questions}

{instruction}"""
    
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