
import asyncio
import google.generativeai as genai
from openai import OpenAI
from typing import Optional, Dict, Any, List
from fastapi import HTTPException
from app.config import settings
from app.utils.base64_to_temp_url import base64_to_temp_url


class LLMClient:
    """Unified client for Gemini and OpenAI multimodal intelligence."""

    def __init__(self):
        self.provider = settings.llm_provider.lower()
        self.gemini_key = settings.gemini_api_key
        self.openai_key = settings.openai_api_key
        self.openai_endpoint = "https://api.openai.com/v1/chat/completions"
        self.gemini_model = settings.gemini_model

        # Configure Gemini SDK globally
        genai.configure(api_key=self.gemini_key)
        # Configure OpenAI SDK globally
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
        
        Please analyze the following transcription and generate QA notes:
        
        TRANSCRIPTION:
        {transcription_text}
        """
        if screenshot_texts:
            prompt += "\n\nSCREENSHOT OCR TEXT:\n"
            for i, text in enumerate(screenshot_texts):
                prompt += f"Screenshot {i+1}: {text}\n"

        # --- QA-specific instructions ---
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

        # --- Format instructions ---
        if format == "markdown":
            prompt += """
            Format your response as a well-structured Markdown document with:
            - A clear title summarizing the feedback session
            - Sections for different types of findings
            - Bullet points for individual issues
            - Code blocks for any technical details
            - A summary section with key takeaways
            """
        else:  # json
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
    # MULTIMODAL ANALYSIS
    # -------------------------------------------------
    async def analyze_multimodal(
        self,
        image_base64: Optional[str] = None,
        text: Optional[str] = None,
        transcription: Optional[str] = None,
        qa_type: str = "general",
        output_format: str = "markdown"
    ) -> Dict[str, Any]:
        """Analyze multimodal input: image, text, and spoken instructions."""
        image_url = None
        if image_base64:
            image_url = await base64_to_temp_url(image_base64)

        combined_text = transcription or text or "(no input)"
        prompt = self._create_prompt(
            transcription_text=combined_text,
            screenshot_texts=[f"Image reference: {image_url}"] if image_url else None,
            qa_type=qa_type,
            format=output_format
        )

        # -------------------------------------------------
        # GEMINI SDK IMPLEMENTATION
        # -------------------------------------------------
        if self.provider == "gemini":
            try:
                model = genai.GenerativeModel(self.gemini_model or "gemini-2.0-flash")
                inputs = [prompt]
                if image_base64:
                    inputs.append({
                        "mime_type": "image/jpeg",
                        "data": image_base64
                    })
                response = await asyncio.to_thread(model.generate_content, inputs)
                text_out = response.text
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Gemini SDK error: {str(e)}")

        # -------------------------------------------------
        # OPENAI FALLBACK
        # -------------------------------------------------
        elif self.provider == "openai":
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are Whispa, a multimodal QA assistant."},
                    {"role": "user", "content": [{"type": "text", "text": prompt}]}
                ]
            )
            text_out = response.choices[0].message.content

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {self.provider}")

        return {"success": True, "response": text_out.strip()}
