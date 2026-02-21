# Instructor Guide - Resume ATS Bootcamp

## Quick Reference for Teaching

---

## 📚 Course Structure

**Total Duration**: ~4.75 hours  
**Format**: Video tutorials + Code-along  
**Level**: Intermediate  
**Prerequisites**: Python basics, command line familiarity

---

## 🎯 Learning Outcomes

By the end, students will have:
1. Complete, production-ready Resume ATS application
2. Understanding of ML/NLP in real-world applications
3. Experience with BERT and spaCy
4. Streamlit UI development skills
5. AWS deployment experience
6. Portfolio project to showcase

---

## 📂 Teaching Materials Provided

### In `teaching/` folder:
- `BOOTCAMP_INDEX.md` - Complete course outline
- `MODULES_OVERVIEW.md` - File-by-file breakdown
- `INSTRUCTOR_GUIDE.md` - This file
- `modules/` - Detailed module scripts

### In `teaching/modules/`:
- `MODULE_00_Introduction.md` - Demo script
- `MODULE_01_System_Architecture.md` - Architecture walkthrough
- `MODULE_02_Environment_Setup.md` - Setup guide
- `MODULE_03_Document_Parser_Part1.md` - Parser basics
- (More modules to be created)

---

## 🎬 Before You Start Recording

### Preparation Checklist:

**Technical Setup**:
- [ ] Screen recording software ready (OBS, Loom, etc.)
- [ ] Audio quality tested (clear microphone)
- [ ] Screen resolution set (1920x1080 recommended)
- [ ] Font size increased for visibility
- [ ] Terminal theme readable
- [ ] IDE/editor configured (VS Code recommended)

**Project Setup**:
- [ ] Fresh clone of repository
- [ ] Virtual environment created
- [ ] All dependencies installed
- [ ] Models downloaded (spaCy, BERT)
- [ ] Sample resumes prepared (3-4 different profiles)
- [ ] Sample job descriptions ready
- [ ] Application tested and working

**Content Preparation**:
- [ ] Module script reviewed
- [ ] Code snippets prepared
- [ ] Diagrams created (architecture, data flow)
- [ ] Talking points memorized
- [ ] Demo flow practiced

---

## 🎤 Recording Tips

### General Guidelines:
1. **Start each module with**:
   - Module number and title
   - What we'll build
   - Why it matters

2. **During coding**:
   - Explain BEFORE typing
   - Type slowly and clearly
   - Explain each line
   - Show errors and how to fix them
   - Test frequently

3. **End each module with**:
   - Quick recap
   - What we built
   - Test the code
   - Preview next module

### Pacing:
- Speak clearly and not too fast
- Pause after important concepts
- Allow time for students to code along
- Show the result frequently

### Common Mistakes to Avoid:
- ❌ Typing too fast
- ❌ Not explaining imports
- ❌ Skipping error handling
- ❌ Not testing code
- ❌ Assuming prior knowledge

---

## 📊 Module-by-Module Guide

### Module 00 (15 min) - Introduction
**Goal**: Get students excited  
**Key**: Show impressive demo, explain real-world problem  
**Tip**: Use real resume examples, show actual match scores

### Module 01 (25 min) - Architecture
**Goal**: Students understand the big picture  
**Key**: Draw clear diagrams, explain data flow  
**Tip**: Use analogies (e.g., "BERT is like a smart translator")

### Module 02 (20 min) - Setup
**Goal**: Everyone has working environment  
**Key**: Show each command, wait for completion  
**Tip**: Mention common errors and solutions

### Module 03 (25 min) - Parser Part 1
**Goal**: First real code, parse documents  
**Key**: Explain PyMuPDF vs other libraries  
**Tip**: Show actual PDF being parsed, print extracted text

### Module 04 (25 min) - Parser Part 2
**Goal**: Extract structured information  
**Key**: Explain regex patterns, show spaCy in action  
**Tip**: Use colorful terminal output to show entities

### Module 05 (25 min) - Parser Part 3
**Goal**: Complete resume structure  
**Key**: Section detection logic, skills matching  
**Tip**: Show before/after of unstructured vs structured data

### Module 06 (20 min) - JD Parser
**Goal**: Parse job descriptions  
**Key**: Similar to resume parsing but simpler  
**Tip**: Use real job postings from LinkedIn/Indeed

### Module 07 (30 min) - BERT Matching ⭐
**Goal**: Core ML - semantic matching  
**Key**: Explain embeddings, cosine similarity  
**Tip**: Show examples: "React" matches "ReactJS" (high score)

### Module 08 (25 min) - Quality Analysis
**Goal**: Score and provide feedback  
**Key**: Explain scoring logic, career levels  
**Tip**: Show how scores change with different resumes

### Module 09 (30 min) - Streamlit UI
**Goal**: Wrap backend in beautiful UI  
**Key**: Streamlit basics, session state  
**Tip**: Show UI updates in real-time

### Module 10 (25 min) - Database & Auth
**Goal**: Add persistence and security  
**Key**: SQLite basics, OAuth flow  
**Tip**: Show profile history, multiple uploads

### Module 11 (30 min) - AWS Deployment
**Goal**: Deploy to production  
**Key**: EB CLI commands, environment variables  
**Tip**: Show live deployed app at the end

---

## 🐛 Common Student Issues

### Setup Issues:
**Problem**: PyMuPDF won't install  
**Solution**: `pip install --upgrade pip`, then retry

**Problem**: spaCy model not found  
**Solution**: `python -m spacy download en_core_web_sm`

**Problem**: Fine-tuned model missing  
**Solution**: App will use base model (mention this is okay)

### Coding Issues:
**Problem**: Import errors  
**Solution**: Check virtual environment is activated

**Problem**: File not found  
**Solution**: Check working directory, use absolute paths

**Problem**: BERT model loading slow  
**Solution**: First time downloads model, be patient

### Deployment Issues:
**Problem**: EB CLI not found  
**Solution**: `pip install awsebcli`

**Problem**: Memory errors on AWS  
**Solution**: Use t2.medium instance or lighter model

---

## 📝 Code Snippets to Have Ready

### Quick Test Commands:
```bash
# Test parser
python test_parser.py uploads/sample_resume.pdf

# Test matcher
python -c "from backend.matcher import _load_model; print(_load_model())"

# Run app
streamlit run streamlit_app.py

# Check imports
python -c "import streamlit, spacy, sentence_transformers; print('✅ All good!')"
```

### Useful Python REPL Tests:
```python
# Test spaCy
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp("John Doe works at Google in California")
for ent in doc.ents:
    print(ent.text, ent.label_)

# Test BERT
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
emb = model.encode("Python Developer")
print(emb.shape)  # (768,)
```

---

## 🎨 Visual Aids to Create

### Diagrams Needed:
1. **System Architecture** (Module 01)
   - Layers: UI → Auth → App → Backend → Storage
   
2. **Data Flow** (Module 01)
   - Upload → Parse → Analyze → Report

3. **BERT Embeddings** (Module 07)
   - Text → Tokens → Embeddings → Similarity

4. **Scoring Breakdown** (Module 08)
   - Components: Skills (25%) + Experience (35%) + etc.

### Tools for Diagrams:
- draw.io (free, easy)
- Excalidraw (hand-drawn style)
- Mermaid (code-based)
- PowerPoint/Keynote

---

## 📦 Files to Provide Students

### Before Course:
- Repository link
- Sample resumes (3-4 PDFs)
- Sample job descriptions (2-3 TXT files)
- Fine-tuned model download link

### During Course:
- Code snippets for each module
- Completed code for reference
- Troubleshooting guide

### After Course:
- Certificate of completion
- Project showcase template
- Further learning resources

---

## 🚀 Post-Course Support

### Encourage Students To:
1. Deploy their own version
2. Add custom features
3. Share on LinkedIn/GitHub
4. Use in portfolio
5. Contribute improvements

### Provide:
- GitHub repo for questions
- Discord/Slack channel
- Office hours (optional)
- Resource list for further learning

---

## 📈 Success Metrics

Students should be able to:
- [ ] Explain how ATS systems work
- [ ] Parse resumes from PDF/DOCX
- [ ] Use spaCy for NER
- [ ] Implement BERT for semantic matching
- [ ] Build Streamlit UI
- [ ] Deploy to AWS
- [ ] Explain their code in interviews

---

## 🎓 Bonus Content Ideas

**For Advanced Students**:
1. Multi-language support
2. Resume template suggestions
3. Interview question generator
4. Salary estimation
5. LinkedIn integration
6. Batch processing
7. API development
8. Docker containerization

---

## 📞 Support Resources

### For Technical Issues:
- Python docs: https://docs.python.org
- Streamlit docs: https://docs.streamlit.io
- spaCy docs: https://spacy.io
- Hugging Face: https://huggingface.co
- AWS EB docs: https://docs.aws.amazon.com/elasticbeanstalk

### For Teaching:
- Code review checklist
- Common error solutions
- FAQ document
- Student feedback form

---

## ✅ Pre-Recording Checklist

**Day Before**:
- [ ] Review module script
- [ ] Test all code
- [ ] Prepare diagrams
- [ ] Check recording setup
- [ ] Get good rest!

**Before Each Module**:
- [ ] Clear terminal history
- [ ] Reset to clean state
- [ ] Open relevant files
- [ ] Test audio/video
- [ ] Take a deep breath!

**After Recording**:
- [ ] Review footage
- [ ] Check audio quality
- [ ] Add timestamps
- [ ] Upload with clear title
- [ ] Add to playlist

---

## 🎬 Video Editing Tips

### Must Include:
- Module title card at start
- Timestamps in description
- Links to code/resources
- Next module preview

### Nice to Have:
- Zoom in on important code
- Highlight cursor
- Add captions
- Background music (subtle)
- Intro/outro animation

---

## 💡 Final Tips

1. **Be enthusiastic** - Your energy is contagious
2. **Make mistakes** - Show how to debug
3. **Explain why** - Not just what
4. **Test often** - Show it working
5. **Encourage questions** - Create community
6. **Celebrate wins** - Each module is progress
7. **Have fun** - You're teaching something cool!

---

## 📧 Contact

For questions about this guide:
- Review module scripts in `teaching/modules/`
- Check `MODULES_OVERVIEW.md` for file details
- Refer to `BOOTCAMP_INDEX.md` for course outline

**Good luck with your bootcamp! You've got this! 🚀**
