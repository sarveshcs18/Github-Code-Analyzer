import vertexai
from vertexai.generative_models import GenerativeModel, Part
from app.core.config import settings
from app.schemas.repo import RepoAnalysisInput, RepoAnalysisResult
from loguru import logger
import json
import asyncio

class GeminiService:
    def __init__(self):
        # Initialize Vertex AI
        if settings.VERTEX_PROJECT_ID:
            vertexai.init(project=settings.VERTEX_PROJECT_ID, location=settings.VERTEX_LOCATION)
            self.model = GenerativeModel("gemini-1.5-pro-001") # Or latest
        else:
            logger.warning("VERTEX_PROJECT_ID not set. Gemini Service will fail if called.")
            self.model = None

    async def analyze_repo(self, input_data: RepoAnalysisInput) -> RepoAnalysisResult:
        if not self.model:
            # Mock response for dev without credentials
            if settings.ENV == "dev":
                logger.info("Returning MOCK Gemini response")
                return self._mock_response()
            raise Exception("Vertex AI not configured")

        prompt = self._construct_prompt(input_data)
        
        try:
            # Run in executor because Vertex SDK might be synchronous or blocking
            # But the new SDK supports async. Let's use run_in_executor to be safe/compatible.
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            ))
            
            response_text = response.text
            # Parse JSON
            data = json.loads(response_text)
            
            # Map request fields if needed or directly validate
            return RepoAnalysisResult(**data)
            
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            raise Exception(f"Gemini analysis failed: {str(e)}")

    def _construct_prompt(self, input_data: RepoAnalysisInput) -> str:
        # Construct context
        files_context = ""
        for name, content in input_data.key_files_content.items():
            files_context += f"\n--- File: {name} ---\n{content}\n"

        structure_list = "\n".join(input_data.structure)

        return f"""
        You are an expert Software Architect. Your task is to analyze the provided GitHub repository structure and key files to generate a comprehensive implementation summary.
        
        Output must be strict JSON matching this schema:
        {{
            "overview": "High-level summary of what the app does.",
            "tech_stack": ["List", "of", "technologies"],
            "architecture": "Description of the architectural pattern (e.g. MVC, Microservices).",
            "modules": [
                {{ "name": "module_name", "description": "What it does" }}
            ],
            "entry_points": ["files or commands to start"],
            "setup_notes": "Instructions on how to build/run."
        }}

        Here is the repository structure:
        {structure_list}

        Here are the key files and their contents:
        {files_context}
        
        Analyze now.
        """

    def _mock_response(self):
        return RepoAnalysisResult(
            overview="[MOCK] This is a mocked response because VERTEX_PROJECT_ID is not set. The app appears to be a Python web server.",
            tech_stack=["Python", "FastAPI", "Docker"],
            architecture="Monolithic REST API",
            modules=[{"name": "app", "description": "Main application logic"}],
            entry_points=["main.py"],
            setup_notes="Run strict commands."
        )

gemini_service = GeminiService()
