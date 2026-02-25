# Module 01: Architecture & Tech Stack (25 min)

## Objective
Students understand the system design and why each technology was chosen.

## Materials Needed
- `docs/ARCHITECTURE_DIAGRAMS.md` (show Mermaid diagrams)
- Whiteboard or digital drawing tool

## Script

### Part 1: High-Level Architecture (8 min)

#### Show Model Architecture Diagram
"Let's break down our system into layers. Each layer has a specific responsibility."

**Frontend Layer (Streamlit)**
"Why Streamlit?
- Rapid development - Python only, no HTML/CSS/JS needed
- Built-in components - file upload, charts, forms
- Session state management
- Perfect for data apps

Alternative: Flask/FastAPI + React (more complex, more control)"

**Authentication Layer**
"Two modes:
- Google OAuth - Production-ready, secure
- Guest mode - Quick testing, no barriers

Why both? User choice. Some want quick access, others want saved history."

**Core Processing Layer**
"This is where the magic happens:
- File Parser: Handles PDF, DOC, DOCX
- spaCy NLP: Extracts entities, sections
- Text Processor: Cleans and structures data

Why spaCy? Fast, accurate, production-ready. Alternative: NLTK (slower, more manual)"

**AI/ML Layer**
"Two models:
1. spaCy (en_core_web_md): Named Entity Recognition, POS tagging
2. Sentence Transformers: Semantic similarity for skill validation

Why Sentence Transformers? 
- Pre-trained on semantic similarity
- Fast inference
- No training needed
- Better than simple keyword matching"

**Scoring Layer**
"Five components, each weighted:
- Formatting (20%): Structure, sections
- Keywords (25%): Industry terms, technical skills
- Content (25%): Action verbs, quantification
- Skills (15%): Proven vs claimed
- ATS (15%): Format compatibility

Why these weights? Based on ATS research and recruiter feedback."

**Data Layer**
"Supabase (PostgreSQL):
- User profiles
- Analysis history
- Resume metadata

Why Supabase? 
- PostgreSQL (reliable, SQL)
- Built-in auth (we use custom, but available)
- Real-time subscriptions
- Free tier for learning"

### Part 2: Tech Stack Deep Dive (10 min)

#### Show Tech Stack Diagram

**Python 3.10**
"Why Python?
- NLP libraries (spaCy, transformers)
- ML ecosystem (PyTorch, scikit-learn)
- Rapid development
- Huge community"

**Streamlit 1.35+**
"Framework for the entire UI. One file can be a complete app."

**spaCy 3.7.4**
"Industrial-strength NLP:
- Tokenization
- POS tagging
- Named Entity Recognition
- Dependency parsing

We use it to extract:
- Skills
- Experience sections
- Contact info
- Keywords"

**Sentence-Transformers**
"Built on BERT. Converts text to 384-dimensional vectors.
Similar meanings = similar vectors.

Example:
'Python developer' and 'Python programming' have high similarity
'Python developer' and 'cooking' have low similarity

This is how we validate skills against project descriptions."

**pdfplumber + python-docx**
"File parsing:
- pdfplumber: Extracts text from PDFs (better than PyPDF2 for complex layouts)
- python-docx: Handles Word documents
- Fallback chain for reliability"

**Supabase**
"PostgreSQL database with:
- REST API
- Real-time subscriptions
- Row-level security
- Built-in auth (optional)"

**AWS Elastic Beanstalk**
"Deployment platform:
- Auto-scaling
- Load balancing
- Health monitoring
- Easy Python app deployment"

### Part 3: Data Flow (7 min)

#### Walk Through Main Workflow Diagram

"Let's trace a resume through the system:

1. **Upload** → File validation (type, size)
2. **Parse** → Extract text (pdfplumber/docx)
3. **Process** → spaCy extracts sections, entities
4. **Validate** → Sentence Transformers check skill claims
5. **Score** → Calculate 5 components
6. **Store** → Save to Supabase
7. **Display** → Render results in Streamlit
8. **Export** → Generate PDF report

Each step has error handling and fallbacks."

### Part 4: Design Decisions (5 min)

**Why Local Models?**
"No API calls to OpenAI/Claude:
- Privacy: Resume data never leaves the server
- Cost: No per-request charges
- Speed: No network latency
- Reliability: No API rate limits

Trade-off: Larger deployment size, need GPU for scale"

**Why Multi-Page App?**
"Streamlit supports:
- Single page: All in one file
- Multi-page: Separate files for each view

We use multi-page for:
- Better organization
- Easier maintenance
- Clear separation of concerns

Note: Has session state quirks (we solved with single-page architecture option)"

**Why Component-Based Scoring?**
"Instead of one black-box score:
- Transparency: Users see what affects their score
- Actionable: Specific feedback per component
- Flexible: Easy to adjust weights
- Debuggable: Can test each component independently"

## Code Files to Reference
- `docs/ARCHITECTURE_DIAGRAMS.md` - All diagrams
- `requirements.txt` - Full dependency list
- `app/` - Project structure

## Key Concepts to Emphasize
1. **Layered architecture** - Separation of concerns
2. **Model selection** - Why these specific libraries
3. **Trade-offs** - Every choice has pros/cons
4. **Production-ready** - Not just "works on my machine"

## Questions for Students
- "Why might we choose local models over API calls?"
- "What are the trade-offs of using Streamlit vs React?"
- "How would you scale this to 10,000 users?"

## Hands-On Activity (Optional)
Draw the architecture on a whiteboard and have students explain each layer.

## Transition to Module 02
"Now that we understand the architecture, let's set up our development environment and create the project structure."
