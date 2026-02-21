# Teaching Materials - Resume ATS Bootcamp

This folder contains all teaching materials for the Resume ATS Analysis System Bootcamp.

---

## 📁 Folder Structure

```
teaching/
├── README.md                          # This file
├── BOOTCAMP_INDEX.md                  # Complete course outline
├── MODULES_OVERVIEW.md                # File-by-file breakdown
├── INSTRUCTOR_GUIDE.md                # Teaching tips and checklist
└── modules/                           # Detailed module scripts
    ├── MODULE_00_Introduction.md
    ├── MODULE_01_System_Architecture.md
    ├── MODULE_02_Environment_Setup.md
    ├── MODULE_03_Document_Parser_Part1.md
    └── ... (more modules)
```

---

## 📚 Documents Overview

### 1. BOOTCAMP_INDEX.md
**Purpose**: Student-facing course outline  
**Contains**:
- Complete module structure (00-11)
- Learning objectives for each module
- Duration and type
- What students will build
- Prerequisites and tech stack
- Learning path diagram

**Use**: Share with students before the course

---

### 2. MODULES_OVERVIEW.md
**Purpose**: Quick reference for file organization  
**Contains**:
- Files to create in each module
- Functions to implement
- Config settings to use
- Testing strategy
- Code reuse patterns
- Timeline of file creation

**Use**: Reference while preparing modules

---

### 3. INSTRUCTOR_GUIDE.md
**Purpose**: Teaching best practices  
**Contains**:
- Recording setup checklist
- Module-by-module teaching tips
- Common student issues and solutions
- Code snippets to have ready
- Visual aids to create
- Pre-recording checklist

**Use**: Read before recording each module

---

### 4. modules/ Directory
**Purpose**: Detailed scripts for each module  
**Contains**:
- `MODULE_00_Introduction.md` - Demo & problem statement
- `MODULE_01_System_Architecture.md` - Architecture walkthrough
- `MODULE_02_Environment_Setup.md` - Setup guide
- `MODULE_03_Document_Parser_Part1.md` - PDF/DOCX parsing
- `MODULE_04_Document_Parser_Part2.md` - NER & contact extraction
- `MODULE_05_to_11_SUMMARY.md` - Quick reference for remaining modules

**Note**: Modules 05-11 are summarized in one document. For detailed implementation, refer to the existing codebase and `MODULES_OVERVIEW.md`.

**Use**: Follow during recording

---

## 🎯 How to Use These Materials

### For Instructors:

**Before Starting**:
1. Read `INSTRUCTOR_GUIDE.md` completely
2. Review `BOOTCAMP_INDEX.md` for course flow
3. Check `MODULES_OVERVIEW.md` for file organization

**For Each Module**:
1. Open the module script in `modules/`
2. Review code to write
3. Prepare diagrams if needed
4. Test the code yourself first
5. Record following the script
6. Test the final result

**After Recording**:
1. Add timestamps to video
2. Upload code to repository
3. Create any supplementary materials
4. Test student experience

---

### For Students:

**Before Course**:
1. Read `BOOTCAMP_INDEX.md` - Course overview
2. Check prerequisites
3. Prepare development environment
4. Download sample files

**During Course**:
1. Follow along with videos
2. Code alongside instructor
3. Test after each module
4. Ask questions in community

**After Course**:
1. Review completed code
2. Deploy your own version
3. Add to portfolio
4. Share your project

---

## 📊 Course Statistics

- **Total Modules**: 12 (00-11)
- **Total Duration**: ~4.75 hours
- **Total Files Created**: ~20 Python files
- **Total Lines of Code**: ~2,500 lines
- **Technologies**: 10+ (Python, Streamlit, BERT, spaCy, AWS, etc.)

---

## 🎓 Module Breakdown

| Module | Title | Duration | Type | Key Files |
|--------|-------|----------|------|-----------|
| 00 | Introduction & Demo | 15 min | Intro | None |
| 01 | System Architecture | 25 min | Design | config.py |
| 02 | Environment Setup | 20 min | Setup | requirements.txt, .env |
| 03 | Parser Part 1 | 25 min | Backend | parser.py, utils.py |
| 04 | Parser Part 2 | 25 min | NLP | parser.py (NER) |
| 05 | Parser Part 3 | 25 min | Backend | parser.py (complete) |
| 06 | JD Parser | 20 min | Backend | jd_parser.py |
| 07 | BERT Matching | 30 min | ML | matcher.py |
| 08 | Quality Analysis | 25 min | Logic | quality_checker.py |
| 09 | Streamlit UI | 30 min | Frontend | streamlit_app.py, ui/ |
| 10 | Database & Auth | 25 min | Full Stack | database.py, auth.py |
| 11 | AWS Deployment | 30 min | DevOps | Procfile, EB config |

---

## 🛠️ Required Tools

### For Recording:
- Screen recording software (OBS, Loom, Camtasia)
- Microphone (good audio quality)
- Code editor (VS Code recommended)
- Terminal with readable theme
- Diagram tool (draw.io, Excalidraw)

### For Development:
- Python 3.8+
- Git
- Virtual environment
- AWS account (for Module 11)
- Google Cloud account (for OAuth - optional)

---

## 📦 Materials to Prepare

### Before Course:
- [ ] Sample resumes (3-4 PDFs with different profiles)
- [ ] Sample job descriptions (2-3 TXT files)
- [ ] Fine-tuned BERT model (upload to cloud storage)
- [ ] Architecture diagrams
- [ ] Data flow diagrams

### During Course:
- [ ] Code repository (GitHub)
- [ ] Completed code for reference
- [ ] Troubleshooting guide
- [ ] FAQ document

### After Course:
- [ ] Certificate template
- [ ] Project showcase guide
- [ ] Further learning resources
- [ ] Community links (Discord/Slack)

---

## 🎬 Recording Workflow

### Preparation:
1. Review module script
2. Test all code
3. Prepare diagrams
4. Set up recording environment
5. Clear terminal history

### Recording:
1. Start with module title
2. Explain what we'll build
3. Code slowly and clearly
4. Test frequently
5. Show errors and fixes
6. End with recap

### Post-Production:
1. Review footage
2. Add timestamps
3. Create thumbnail
4. Write description
5. Upload to platform
6. Add to playlist

---

## 💡 Teaching Tips

### Do:
- ✅ Explain before typing
- ✅ Show the result frequently
- ✅ Make intentional mistakes
- ✅ Test after each section
- ✅ Use real-world examples
- ✅ Encourage questions

### Don't:
- ❌ Type too fast
- ❌ Skip error handling
- ❌ Assume prior knowledge
- ❌ Rush through concepts
- ❌ Forget to test
- ❌ Use jargon without explaining

---

## 🐛 Common Issues & Solutions

### Setup Issues:
- **PyMuPDF won't install**: Update pip first
- **spaCy model not found**: Run download command
- **Virtual env not activating**: Check path

### Coding Issues:
- **Import errors**: Check venv is activated
- **File not found**: Use absolute paths
- **Model loading slow**: First download takes time

### Deployment Issues:
- **EB CLI not found**: Install awsebcli
- **Memory errors**: Use larger instance
- **OAuth errors**: Check redirect URLs

---

## 📈 Success Criteria

Students should be able to:
- [ ] Parse resumes from multiple formats
- [ ] Extract structured information with NLP
- [ ] Implement semantic matching with BERT
- [ ] Build interactive UI with Streamlit
- [ ] Deploy to AWS
- [ ] Explain the system architecture
- [ ] Debug common issues
- [ ] Extend with new features

---

## 🔗 Additional Resources

### Documentation:
- [Python Docs](https://docs.python.org)
- [Streamlit Docs](https://docs.streamlit.io)
- [spaCy Docs](https://spacy.io)
- [Hugging Face](https://huggingface.co)
- [AWS EB Docs](https://docs.aws.amazon.com/elasticbeanstalk)

### Learning:
- BERT paper: "Attention is All You Need"
- NLP course: fast.ai
- Streamlit tutorials: YouTube
- AWS tutorials: AWS Training

---

## 📞 Support

### For Instructors:
- Review `INSTRUCTOR_GUIDE.md` for detailed tips
- Check module scripts for specific guidance
- Test all code before recording

### For Students:
- Follow `BOOTCAMP_INDEX.md` for course structure
- Use module materials as reference
- Join community for questions

---

## 🚀 Next Steps

1. **Read** `INSTRUCTOR_GUIDE.md`
2. **Review** `BOOTCAMP_INDEX.md`
3. **Check** `MODULES_OVERVIEW.md`
4. **Prepare** sample files and diagrams
5. **Test** all code yourself
6. **Record** Module 00 first
7. **Iterate** based on feedback

---

## ✅ Pre-Launch Checklist

- [ ] All module scripts completed
- [ ] Sample files prepared
- [ ] Fine-tuned model hosted
- [ ] Diagrams created
- [ ] Code tested end-to-end
- [ ] Recording setup tested
- [ ] Community platform ready
- [ ] Marketing materials prepared

---

**Ready to teach? Let's build something amazing! 🎓🚀**
