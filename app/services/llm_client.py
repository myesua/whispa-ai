import os
import io
import base64
from google.genai import Client 
from openai import OpenAI
from typing import Optional, List, AsyncGenerator
from fastapi import HTTPException
from app.config import settings

class LLMClient:
    """Unified client for Gemini and OpenAI multimodal intelligence."""

    def __init__(self):
        self.provider = settings.llm_provider.lower()
        self.openai_key = settings.openai_api_key
        
        if settings.gemini_api_key:
            self.client = Client(api_key=settings.gemini_api_key) 
            self.aclient = self.client.aio
            # self.gemini_model = settings.gemini_model or "gemini-2.5-flash"
            self.gemini_model = "gemini-2.5-flash"
        else:
            self.client = None
            self.aclient = None
            self.gemini_model = "gemini-2.5-flash"

        self.openai_endpoint = "https://api.openai.com/v1/chat/completions"
        self.openai_client = OpenAI(api_key=self.openai_key)

    # -------------------------------------------------
    # PROMPT BUILDER
    # -------------------------------------------------
    @staticmethod
    def _create_prompt(
        transcription_text: str,
        screenshot_texts: Optional[List[str]] = None,
        qa_type: str = "general",
        format: str = "markdown"
    ) -> str:
        """Generate a rich, structured QA prompt for Whispa assistant."""
        prompt = f"""
        You are Whispa, an AI QA assistant that helps generate insightful notes from user feedback sessions.
        **CRITICAL INSTRUCTION: Do not include any introductory phrases, greetings, or conversational filler (e.g., "Of course!", "As an AI..."). Start your response immediately with the formatted analysis.**
        Please analyze the following transcription and generate QA notes:
        
        TRANSCRIPTION:
        {transcription_text}
        """
        if screenshot_texts:
            prompt += "\n\nCRITICAL: Analyze the images provided in this request against the context of the transcription."

        if qa_type == "bug":
            prompt += """
            Focus on identifying bugs and technical issues mentioned in the feedback.
            For each bug, extract:
            1. A clear description of the issue
            2. Steps to reproduce (if mentioned)
            3. Impact or severity
            4. Any context about when it occurs
            """
        elif qa_type == "ux":
            prompt += """
            Focus on user experience issues and feedback mentioned in the transcription.
            For each UX issue, extract:
            1. A clear description of the usability problem
            2. User sentiment or frustration level
            3. Impact on user workflow
            4. Any suggestions for improvement mentioned
            """
        elif qa_type == "feature":
            prompt += """
            Focus on feature requests and enhancement suggestions mentioned in the feedback.
            For each feature request, extract:
            1. A clear description of the requested feature
            2. The user need or problem it would solve
            3. Priority or importance (if mentioned)
            4. Any specific implementation details suggested
            """
        else:
            prompt += """
            Provide a comprehensive analysis of the feedback, including:
            1. Key issues identified (bugs, UX problems, etc.)
            2. Feature requests or enhancement suggestions
            3. User sentiment and pain points
            4. Prioritized recommendations based on user impact
            """

        if format == "markdown":
            prompt += """
            Format your response as a well-structured Markdown document with:
            - A clear title summarizing the feedback session
            - Sections for different types of findings
            - Bullet points for individual issues
            - Code blocks for any technical details
            - A summary section with key takeaways
            """
        else: 
            prompt += """
            Format your response as a valid JSON object with the following structure:
            {
              "title": "Summary title",
              "observations": [
                {
                  "type": "bug|ux|feature",
                  "description": "Clear description",
                  "severity": "high|medium|low",
                  "details": "Additional context",
                  "recommendations": "Suggested actions"
                }
              ],
              "summary": "Overall summary text"
            }
            Ensure the JSON is valid and properly formatted.
            """
        return prompt.strip()

    # -------------------------------------------------
    # MULTIMODAL ANALYSIS (STREAMING)
    # -------------------------------------------------
    async def analyze_multimodal(
        self,
        images_base64: Optional[list[str]] = None,
        text: Optional[str] = None,
        transcription: Optional[str] = None,
        qa_type: str = "general",
        output_format: str = "markdown",
        image_file: str = None,
    ) -> AsyncGenerator[str, None]:
        """Analyze multimodal input and stream the response."""
        
        temp_file_path = None
        uploaded_files_map = {} 

        try:
            combined_text = transcription or text or "(no input)"
            
            if self.provider == "gemini":
                if not self.aclient:
                     raise HTTPException(status_code=500, detail="Gemini client not initialized. Check GEMINI_API_KEY in settings.")

                uploaded_file_objects = []
                screenshot_texts = [] 

                if images_base64:
                    for i, image_base64 in enumerate(images_base64):
                        if image_base64.startswith('data:image'):
                            image_base64 = image_base64.split(',')[1]
                        
                        try:
                            image_bytes = base64.b64decode(image_base64)
                            image_file_like = io.BytesIO(image_bytes)

                            uploaded_file = await self.aclient.files.upload(
                                file=image_file_like,
                                config={
                                    'mime_type': 'image/jpeg' 
                                }
                            )
                            uploaded_file_objects.append(uploaded_file)
                            uploaded_files_map[uploaded_file.name] = uploaded_file 
                            screenshot_texts.append(f"Image {i+1}")
                            
                        except Exception as e:
                            if uploaded_files_map:
                                for name in uploaded_files_map:
                                    await self.aclient.files.delete(name=name)
                            raise HTTPException(status_code=500, detail=f"In-memory image upload failed: {str(e)}")
                            
                elif image_file:
                    uploaded_file = await self.aclient.files.upload(
                        file=image_file
                    )
                    uploaded_file_objects.append(uploaded_file)
                    uploaded_files_map[uploaded_file.name] = uploaded_file 
                    screenshot_texts = ["Image 1"]

                prompt_text = self._create_prompt(
                    transcription_text=combined_text,
                    screenshot_texts=screenshot_texts, 
                    qa_type=qa_type,
                    format=output_format
                )

                contents = [prompt_text]
                contents.extend(uploaded_file_objects) 
                
                response_stream = await self.aclient.models.generate_content_stream(
                    model=self.gemini_model,
                    contents=contents
                )

                async for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text
        
            elif self.provider == "openai":
                prompt_text = self._create_prompt(
                    transcription_text=combined_text,
                    screenshot_texts=None, 
                    qa_type=qa_type,
                    format=output_format
                )
            
                stream = await self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are Whispa, a multimodal QA assistant."},
                        {"role": "user", "content": prompt_text} 
                    ],
                    stream=True
                )
                async for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content

            else:
                raise HTTPException(status_code=400, detail=f"Unsupported provider: {self.provider}")

        finally:
            if uploaded_files_map and self.aclient:
                for name in uploaded_files_map:
                    try:
                        await self.aclient.files.delete(name=name) 
                    except Exception as e:
                        print(f"Failed to delete uploaded file {name}: {e}") 
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)