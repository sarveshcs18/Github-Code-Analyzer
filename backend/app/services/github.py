import os
import shutil
import tempfile
import asyncio
import subprocess
from app.core.config import settings
from app.schemas.repo import RepoAnalysisInput
from loguru import logger
from pathlib import Path

class GitHubService:
    def __init__(self):
        self.tmp_dir = tempfile.gettempdir()

    async def clone_and_analyze(self, repo_url: str) -> RepoAnalysisInput:
        target_dir = tempfile.mkdtemp(prefix="repo_")
        try:
            logger.info(f"Cloning {repo_url} into {target_dir}")
            await self._clone_repo(repo_url, target_dir)
            analysis = await self._analyze_dir(target_dir)
            return analysis
        finally:
            # Cleanup
            logger.info(f"Cleaning up {target_dir}")
            # shutil.rmtree(target_dir, ignore_errors=True) 
            # Note: In prod we should clean up. For debugging, maybe keep?
            # Keeping 'ignore_errors' to avoid permission issues.
            shutil.rmtree(target_dir, ignore_errors=True)

    async def _clone_repo(self, url: str, target_dir: str):
        # Construct SSH command if key is present
        env = os.environ.copy()
        if settings.SSH_KEY_PATH and os.path.exists(settings.SSH_KEY_PATH):
            logger.info("Using custom SSH key provided in settings")
            # Strict host key checking=no for simplicity in internal envs, or use known_hosts
            env["GIT_SSH_COMMAND"] = f"ssh -i {settings.SSH_KEY_PATH} -o StrictHostKeyChecking=no"
        
        # Run git clone
        # Using subprocess for better control over environment variables (SSH key)
        cmd = ["git", "clone", "--depth", "1", url, target_dir]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Git clone failed: {stderr.decode()}")
            raise Exception(f"Failed to clone repository: {stderr.decode()}")

    async def _analyze_dir(self, directory: str) -> RepoAnalysisInput:
        structure = []
        key_files = {} # filename -> content
        languages = {}

        # Files of interest for "key_files"
        INTERESTING_FILES = {
            "requirements.txt", "package.json", "setup.py", "Dockerfile", 
            "README.md", "pyproject.toml", "go.mod", "Cargo.toml", "pom.xml"
        }
        
        # Limits
        MAX_FILE_SIZE = 100 * 1024 # 100KB for content reading
        
        for root, dirs, files in os.walk(directory):
            # Skip .git
            if ".git" in dirs:
                dirs.remove(".git")
            
            rel_root = os.path.relpath(root, directory)
            if rel_root == ".":
                rel_root = ""
            
            for f in files:
                full_path = os.path.join(root, f)
                rel_path = os.path.join(rel_root, f) if rel_root else f
                
                structure.append(rel_path)
                
                # Extension stats
                _, ext = os.path.splitext(f)
                if ext:
                    languages[ext] = languages.get(ext, 0) + 1
                
                # Content reading
                if f in INTERESTING_FILES:
                    try:
                        if os.path.getsize(full_path) < MAX_FILE_SIZE:
                            with open(full_path, "r", errors="ignore") as f_obj:
                                key_files[f] = f_obj.read()
                    except Exception as e:
                        logger.warning(f"Failed to read {f}: {e}")

        # Limit structure list size for prompt optimization?
        # For now, take top 500 files or something? 
        # Or just pass raw. Gemini 1.5 Pro has huge context window.
        
        return RepoAnalysisInput(
            structure=structure[:2000],  # Limit strictly to avoid explosions
            key_files_content=key_files,
            languages=languages
        )
        
github_service = GitHubService()
