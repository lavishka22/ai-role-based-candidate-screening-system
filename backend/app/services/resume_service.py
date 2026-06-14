import re
from pathlib import Path
from pypdf import PdfReader

COMMON_SKILLS = [
    "python", "java", "javascript", "typescript", "sql", "fastapi", "flask", "django",
    "react", "next.js", "node", "postgresql", "mysql", "mongodb", "docker", "kubernetes",
    "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "pandas",
    "numpy", "opencv", "nlp", "rag", "llm", "mlflow", "git", "github actions", "aws",
    "rest api", "microservices", "system design", "data structures", "algorithms"
]

ROLE_TOPICS = {
    "AI/ML Engineer": ["machine learning", "model evaluation", "feature engineering", "deep learning", "RAG", "embeddings", "MLOps"],
    "Backend Engineer": ["REST API", "databases", "authentication", "system design", "caching", "queues", "scalability"],
}

def extract_text_from_upload(filename: str, data: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        temp = Path("temp_resume.pdf")
        temp.write_bytes(data)
        reader = PdfReader(str(temp))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        temp.unlink(missing_ok=True)
        return text.strip()
    return data.decode("utf-8", errors="ignore").strip()

def parse_resume(text: str) -> dict:
    lowered = text.lower()
    skills = sorted({skill for skill in COMMON_SKILLS if skill in lowered})
    emails = re.findall(r"[\w\.-]+@[\w\.-]+", text)
    github = re.findall(r"https?://github\.com/[^\s]+", text, flags=re.I)
    projects = []
    for line in text.splitlines():
        if any(word in line.lower() for word in ["project", "dashboard", "system", "detection", "analytics"]):
            cleaned = line.strip(" -•\t")
            if 8 < len(cleaned) < 130:
                projects.append(cleaned)
    return {
        "skills": skills,
        "emails": emails[:2],
        "github": github[:3],
        "projects": projects[:8],
        "seniority_hint": "fresher/intern" if len(skills) < 12 else "junior",
    }

def build_dynamic_queries(role: str, profile: dict) -> list[str]:
    role_topics = ROLE_TOPICS.get(role, ROLE_TOPICS["AI/ML Engineer"])
    skills = profile.get("skills", [])[:8]
    projects = profile.get("projects", [])[:3]
    queries = []
    for topic in role_topics:
        queries.append(f"{role} interview concepts for {topic} with candidate skills {' '.join(skills)}")
    for project in projects:
        queries.append(f"{role} applied question related to project {project}")
    return queries[:8]
