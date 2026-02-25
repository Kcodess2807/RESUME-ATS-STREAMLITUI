# Module 00: Intro & Demo (15 min)

## Objective
Give students a complete overview of what they'll build and why it matters.

## Script

### Opening (2 min)
"Welcome! Over the next few hours, we're going to build a production-ready ATS Resume Scorer. This isn't a toy project - it's a real application that uses NLP, machine learning, and modern web technologies to solve a genuine problem: helping job seekers optimize their resumes for Applicant Tracking Systems."

### The Problem (3 min)
"Here's the reality: 75% of resumes never reach human eyes. They're filtered out by ATS software. Why?
- Wrong keywords
- Poor formatting
- Skills mentioned but not proven
- Missing quantifiable achievements

Our app solves this by analyzing resumes across 5 dimensions and giving actionable feedback."

### Live Demo Walkthrough (8 min)

#### 1. Landing Page
"Notice the clean, professional UI. This is built with Streamlit - we'll see how easy it is to create this."

#### 2. Authentication
"We support both Google OAuth and Guest mode. This teaches you real-world authentication patterns."

#### 3. Upload Resume
"Drag and drop a resume. Behind the scenes:
- File validation (PDF/DOC/DOCX)
- Text extraction
- NLP processing
- ML-based skill validation"

#### 4. Results Dashboard
"Look at the score breakdown:
- Formatting: 20% - Is it ATS-friendly?
- Keywords: 25% - Right industry terms?
- Content: 25% - Action verbs, quantification?
- Skills: 15% - Are skills proven in projects?
- ATS Compatibility: 15% - Will it pass automated filters?

Each component has specific feedback."

#### 5. Skill Validation (Key Feature)
"This is where ML shines. We use BERT embeddings to check if skills are actually demonstrated in projects. Not just keyword matching - semantic understanding."

#### 6. JD Comparison
"Upload a job description and see:
- Missing keywords
- Skill gaps
- Semantic similarity score"

#### 7. PDF Report
"Generate a professional report with all findings."

### What You'll Learn (2 min)
"By the end, you'll know:
- Document parsing (PDF/DOCX)
- NLP with spaCy
- ML with Sentence Transformers
- Streamlit for rapid UI development
- Database integration with Supabase
- OAuth authentication
- AWS deployment

Let's dive in!"

## Demo Checklist
- [ ] Show landing page
- [ ] Demonstrate Google login
- [ ] Upload sample resume
- [ ] Walk through each score component
- [ ] Show skill validation details
- [ ] Compare with job description
- [ ] Download PDF report
- [ ] Show history page
- [ ] Explain the value proposition

## Key Points to Emphasize
1. **Real-world application** - Not a tutorial project
2. **Production-ready** - Authentication, database, deployment
3. **ML/NLP integration** - Not just CRUD
4. **Modern stack** - Current best practices
5. **Scalable architecture** - Can handle real users

## Questions to Ask Students
- "Who has applied for jobs recently?"
- "Have you heard of ATS systems?"
- "What do you think makes a resume ATS-friendly?"

## Transition to Module 01
"Now that you've seen what we're building, let's understand the architecture and technology choices behind it."
