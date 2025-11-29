# Implementation Plan

- [x] 1. Set up project structure and dependencies
  - Create directory structure for pages, utils, data, assets, and models
  - Create requirements.txt with all necessary packages
  - Create .streamlit/config.toml with theme configuration
  - Create .gitignore file
  - Set up virtual environment and install dependencies
  - Download and cache required models (spaCy, NLTK data)
  - _Requirements: 14.1, 14.2, 14.3, 16.1_

- [x] 2. Implement file parsing module
  - Create utils/file_parser.py with file validation and text extraction functions
  - Implement PDF parsing with pdfplumber (primary) and PyPDF2 (fallback)
  - Implement DOC/DOCX parsing with python-docx
  - Add file type validation (magic number checking)
  - Add file size validation (5MB limit)
  - Implement error handling with specific error messages
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 15.1, 15.2_

- [ ] 2.1 Write property test for file type validation
  - **Property 6: File type validation**
  - **Validates: Requirements 3.1**

- [ ] 2.2 Write property test for file size limit
  - **Property 7: File size limit enforcement**
  - **Validates: Requirements 3.2**

- [ ] 2.3 Write property test for text extraction
  - **Property 8: Text extraction from valid files**
  - **Validates: Requirements 3.3, 3.4**

- [ ] 2.4 Write property test for extraction error handling
  - **Property 9: Extraction failure error handling**
  - **Validates: Requirements 3.5**

- [ ] 2.5 Write unit tests for file parser edge cases
  - Test corrupted files, empty files, various encodings
  - Test PDF and DOCX with different formatting
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 3. Implement NLP text processor module
  - Create utils/text_processor.py with NLP processing functions
  - Initialize and cache spaCy model using @st.cache_resource
  - Implement section extraction (summary, experience, education, skills, projects)
  - Implement contact information extraction (email, phone, LinkedIn, GitHub, portfolio)
  - Implement skills extraction with technical and soft skills categorization
  - Implement project extraction with title and description parsing
  - Implement keyword extraction using spaCy NER and frequency analysis
  - Implement action verb detection
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 14.1, 14.4, 16.1_

- [ ] 3.1 Write property test for section extraction
  - **Property 14: Comprehensive section extraction**
  - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6**

- [ ] 3.2 Write unit tests for text processor components
  - Test contact info extraction with various formats
  - Test keyword extraction accuracy
  - Test action verb detection
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [x] 4. Implement skill validator module
  - Create utils/skill_validator.py with skill validation functions
  - Initialize and cache Sentence-Transformers model using @st.cache_resource
  - Implement exact skill matching in project descriptions
  - Implement semantic similarity calculation using embeddings
  - Implement validation threshold logic (0.6 threshold)
  - Implement skill-project mapping generation
  - Implement validation score calculation: (validated / total) × 15
  - Generate validation feedback messages
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 14.2, 14.4_

- [ ]* 4.1 Write property test for exact skill matching
  - **Property 15: Exact skill matching**
  - **Validates: Requirements 6.1**

- [ ]* 4.2 Write property test for semantic similarity calculation
  - **Property 16: Semantic similarity calculation**
  - **Validates: Requirements 6.2**

- [ ]* 4.3 Write property test for similarity threshold
  - **Property 17: Similarity threshold validation**
  - **Validates: Requirements 6.3**

- [ ]* 4.4 Write property test for unmatched skill detection
  - **Property 18: Unmatched skill detection**
  - **Validates: Requirements 6.4**

- [ ]* 4.5 Write property test for skill-project mapping
  - **Property 19: Skill-project mapping completeness**
  - **Validates: Requirements 6.5**

- [ ]* 4.6 Write property test for skill validation score formula
  - **Property 20: Skill validation score formula**
  - **Validates: Requirements 6.6**

- [ ]* 4.7 Write unit tests for skill validator edge cases
  - Test with no skills, no projects, empty descriptions
  - Test threshold boundary cases (0.59, 0.6, 0.61)
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [x] 5. Implement grammar checker module
  - Create utils/grammar_checker.py with grammar checking functions
  - Initialize and cache LanguageTool using @st.cache_resource
  - Implement comprehensive grammar and spelling check
  - Implement error categorization (critical, moderate, minor)
  - Implement correction suggestion extraction
  - Implement grammar penalty calculation: 5×critical + 2×moderate + 0.5×minor (max 20)
  - Add technical term whitelist to avoid false positives
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 14.3, 14.4_

- [ ]* 5.1 Write property test for comprehensive error detection
  - **Property 21: Comprehensive error detection**
  - **Validates: Requirements 7.1, 7.2, 7.3**

- [ ]* 5.2 Write property test for error categorization
  - **Property 22: Error categorization completeness**
  - **Validates: Requirements 7.4**

- [ ]* 5.3 Write property test for error correction suggestions
  - **Property 23: Error correction suggestions**
  - **Validates: Requirements 7.5**

- [ ]* 5.4 Write property test for grammar penalty calculation
  - **Property 24: Grammar penalty calculation**
  - **Validates: Requirements 7.6**

- [ ]* 5.5 Write unit tests for grammar checker
  - Test with known spelling errors
  - Test penalty cap at 20 points
  - Test technical term whitelist
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [x] 6. Implement location detector module
  - Create utils/location_detector.py with location detection functions
  - Implement address detection using spaCy NER (GPE, LOC tags)
  - Implement regex patterns for various address formats
  - Implement zip code detection (5-digit and 9-digit)
  - Implement contact header exemption logic
  - Implement privacy risk assessment
  - Generate location removal recommendations
  - Calculate privacy penalty (3-5 points)
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [ ]* 6.1 Write property test for address detection
  - **Property 25: Address detection**
  - **Validates: Requirements 8.1, 8.2, 8.3**

- [ ]* 6.2 Write property test for contact header exemption
  - **Property 26: Contact header exemption**
  - **Validates: Requirements 8.4**

- [ ]* 6.3 Write property test for location recommendations
  - **Property 27: Location recommendation generation**
  - **Validates: Requirements 8.5**

- [ ]* 6.4 Write property test for location privacy penalty
  - **Property 28: Location privacy penalty**
  - **Validates: Requirements 8.6**

- [ ]* 6.5 Write unit tests for location detector
  - Test various address formats (US, international)
  - Test edge cases (city names that are common words)
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [x] 7. Implement scoring engine module
  - Create utils/scorer.py with scoring calculation functions
  - Implement formatting score calculation (0-20 points)
  - Implement keywords and skills score calculation (0-25 points)
  - Implement content quality score calculation (0-25 points)
  - Implement skill validation score calculation (0-15 points)
  - Implement ATS compatibility score calculation (0-15 points)
  - Implement overall score aggregation with penalties and bonuses
  - Ensure all scores are bounded within their ranges
  - Generate score interpretation messages
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [ ]* 7.1 Write property test for component score bounds
  - **Property 29: Component score bounds**
  - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**

- [ ]* 7.2 Write property test for overall score aggregation
  - **Property 30: Overall score aggregation**
  - **Validates: Requirements 9.6, 9.7**

- [ ]* 7.3 Write unit tests for scoring engine
  - Test each component score calculation
  - Test penalty and bonus application
  - Test score bounds enforcement
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [x] 8. Implement job description comparison module
  - Add JD keyword extraction to text_processor.py
  - Implement semantic similarity calculation between resume and JD
  - Implement matched keyword identification
  - Implement missing keyword identification
  - Implement skills gap analysis
  - Calculate match percentage (0-100)
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ]* 8.1 Write property test for bidirectional keyword extraction
  - **Property 31: Bidirectional keyword extraction**
  - **Validates: Requirements 10.1**

- [ ]* 8.2 Write property test for semantic similarity bounds
  - **Property 32: Semantic similarity bounds**
  - **Validates: Requirements 10.2**

- [ ]* 8.3 Write property test for keyword intersection
  - **Property 33: Keyword intersection identification**
  - **Validates: Requirements 10.3**

- [ ]* 8.4 Write property test for missing keyword identification
  - **Property 34: Missing keyword identification**
  - **Validates: Requirements 10.4**

- [ ]* 8.5 Write property test for match percentage bounds
  - **Property 35: Match percentage bounds**
  - **Validates: Requirements 10.5**

- [ ]* 8.6 Write unit tests for JD comparison
  - Test with various resume-JD pairs
  - Test edge cases (no overlap, complete overlap)
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 9. Implement authentication system
  - Create utils/auth.py with authentication functions
  - Choose authentication method (Google OAuth or streamlit-authenticator)
  - Implement login functionality with session creation
  - Implement logout functionality with session termination
  - Implement session persistence and expiration
  - Implement protected page redirect logic
  - Display user information in sidebar
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 9.1 Write property test for unauthenticated access protection
  - **Property 1: Unauthenticated access protection**
  - **Validates: Requirements 2.1**

- [ ]* 9.2 Write property test for valid credential acceptance
  - **Property 2: Valid credential acceptance**
  - **Validates: Requirements 2.2**

- [ ]* 9.3 Write property test for session information display
  - **Property 3: Session information display**
  - **Validates: Requirements 2.3**

- [ ]* 9.4 Write property test for logout session termination
  - **Property 4: Logout session termination**
  - **Validates: Requirements 2.4**

- [ ]* 9.5 Write property test for expired session re-authentication
  - **Property 5: Expired session re-authentication**
  - **Validates: Requirements 2.5**

- [ ]* 9.6 Write unit tests for authentication
  - Test login with valid/invalid credentials
  - Test session expiration timing
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 10. Create landing page
  - Create Home.py as the main landing page
  - Implement hero section with compelling headline and CTA button
  - Create features overview section with 3 columns and icons
  - Create how-it-works section with 3-step numbered process
  - Create benefits section highlighting key advantages
  - Add testimonials or stats section
  - Create footer with links
  - Add custom CSS for styling and animations
  - Implement navigation to ATS scorer page
  - _Requirements: 1.1, 1.2, 1.4, 1.5_

- [ ]* 10.1 Write unit tests for landing page
  - Test that all sections are present
  - Test CTA button navigation
  - _Requirements: 1.1, 1.2, 1.4, 1.5_

- [x] 11. Implement progress indicator system
  - Create progress tracking in session state
  - Implement progress bar component with percentage display
  - Define all processing stages with emojis
  - Implement progress update function
  - Add smooth progress bar animations
  - Display current stage name and emoji
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ]* 11.1 Write property test for progress initialization
  - **Property 10: Progress initialization**
  - **Validates: Requirements 4.1**

- [ ]* 11.2 Write property test for progress monotonicity
  - **Property 11: Progress monotonicity**
  - **Validates: Requirements 4.2**

- [ ]* 11.3 Write property test for progress completion
  - **Property 12: Progress completion**
  - **Validates: Requirements 4.3**

- [ ]* 11.4 Write property test for stage identification
  - **Property 13: Stage identification**
  - **Validates: Requirements 4.4**

- [x] 12. Create main ATS scorer page
  - Create pages/1_🎯_ATS_Scorer.py
  - Implement authentication check and redirect
  - Create mode selection (General ATS Score vs JD Comparison)
  - Implement file upload component for resume
  - Implement optional file upload for job description
  - Wire up file validation and parsing
  - Integrate progress indicator
  - Wire up all analysis modules (text processor, skill validator, grammar checker, location detector)
  - Wire up scoring engine
  - Handle errors gracefully with user-friendly messages
  - _Requirements: 2.1, 3.1, 3.2, 4.1, 4.2, 4.3, 4.4, 15.3, 15.4_

- [ ]* 12.1 Write property test for no external API calls
  - **Property 51: No external API calls**
  - **Validates: Requirements 14.5**

- [ ]* 12.2 Write integration tests for analysis flow
  - Test end-to-end: upload → extract → process → score
  - Test with 5+ real resume samples
  - _Requirements: 3.1, 3.2, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [x] 13. Implement results dashboard
  - Create overall score display with color coding (red < 60, yellow 60-79, green ≥ 80)
  - Create score breakdown section with progress bars for all 5 components
  - Create strengths section with expandable details
  - Create critical issues section with expandable details
  - Create areas for improvement section
  - Create recommendations section
  - _Requirements: 11.1, 11.2_

- [ ]* 13.1 Write property test for score color coding
  - **Property 36: Score color coding**
  - **Validates: Requirements 11.1**

- [ ]* 13.2 Write property test for component score display
  - **Property 37: Component score display completeness**
  - **Validates: Requirements 11.2**

- [x] 14. Implement skill validation display section
  - Create skill validation analysis section in results dashboard
  - Display validated skills with associated project names
  - Display unvalidated skills with warning indicators
  - Create skill-project matrix visualization
  - Generate and display validation feedback messages
  - _Requirements: 11.3, 11.4_

- [ ]* 14.1 Write property test for skill validation display
  - **Property 38: Skill validation display**
  - **Validates: Requirements 11.3**

- [ ]* 14.2 Write property test for unvalidated skill warnings
  - **Property 39: Unvalidated skill warnings**
  - **Validates: Requirements 11.4**

- [x] 15. Implement grammar check display section
  - Create grammar and spelling analysis section in results dashboard
  - Display all errors categorized by severity (critical, moderate, minor)
  - Show correction suggestions for each error
  - Display error locations and context
  - Create summary metrics (total errors, error-free sections)
  - _Requirements: 11.5_

- [ ]* 15.1 Write property test for grammar error display
  - **Property 40: Grammar error display**
  - **Validates: Requirements 11.5**

- [x] 16. Implement privacy check display section
  - Create privacy and location check section in results dashboard
  - Display privacy alert with color coding based on risk level
  - Show detected locations with section information
  - Display removal recommendations
  - Show privacy status (issue detected, warning, optimized)
  - _Requirements: 11.6_

- [ ]* 16.1 Write property test for privacy alert display
  - **Property 41: Privacy alert display**
  - **Validates: Requirements 11.6**

- [x] 17. Implement JD comparison display section
  - Create keyword analysis section (conditional on JD provided)
  - Display matched keywords with visualization
  - Display missing critical keywords with importance
  - Display skills gap analysis
  - Show match percentage and semantic similarity
  - _Requirements: 11.7_

- [ ]* 17.1 Write property test for JD comparison display
  - **Property 42: JD comparison display**
  - **Validates: Requirements 11.7**

- [x] 18. Implement action items section
  - Create priority action items section in results dashboard
  - Display items categorized by priority (critical, high, medium)
  - Use color coding for priority levels
  - Format as interactive checklist
  - _Requirements: 11.8_

- [ ]* 18.1 Write property test for action item prioritization display
  - **Property 43: Action item prioritization display**
  - **Validates: Requirements 11.8**

- [x] 19. Implement recommendation generation system
  - Create utils/recommendation_generator.py
  - Implement recommendation generation for unvalidated skills
  - Implement recommendation generation for grammar errors
  - Implement recommendation generation for location privacy issues
  - Implement recommendation generation for missing keywords
  - Implement recommendation generation for formatting issues
  - Implement recommendation prioritization by impact
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6_

- [ ]* 19.1 Write property test for issue-specific recommendations
  - **Property 44: Issue-specific recommendation generation**
  - **Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5**

- [ ]* 19.2 Write property test for recommendation prioritization
  - **Property 45: Recommendation prioritization**
  - **Validates: Requirements 12.6**

- [x] 20. Implement report generation module
  - Create utils/report_generator.py
  - Implement PDF report generation with fpdf or ReportLab
  - Include overall score and all component breakdowns in PDF
  - Include all recommendations and action items in PDF
  - Include visualizations (score charts, keyword analysis)
  - Implement action items checklist generation
  - Add download buttons in UI
  - _Requirements: 13.1, 13.2, 13.3, 13.4_

- [ ]* 20.1 Write property test for PDF report completeness
  - **Property 46: PDF report completeness**
  - **Validates: Requirements 13.1, 13.2**

- [ ]* 20.2 Write property test for PDF visualization inclusion
  - **Property 47: PDF visualization inclusion**
  - **Validates: Requirements 13.3**

- [ ]* 20.3 Write property test for action items checklist generation
  - **Property 48: Action items checklist generation**
  - **Validates: Requirements 13.4**

- [ ]* 20.4 Write unit tests for report generation
  - Test PDF generation with various analysis results
  - Test checklist generation
  - _Requirements: 13.1, 13.2, 13.3, 13.4_

- [x] 21. Implement model caching and performance optimization
  - Add @st.cache_resource decorators for all model loading functions
  - Add @st.cache_data decorators for expensive computations
  - Implement result caching for identical resumes
  - Optimize text processing for speed
  - Add lazy loading for optional features
  - _Requirements: 14.4, 16.1, 16.2_

- [ ]* 21.1 Write property test for local model initialization
  - **Property 49: Local model initialization**
  - **Validates: Requirements 14.1, 14.2, 14.3**

- [ ]* 21.2 Write property test for model caching
  - **Property 50: Model caching**
  - **Validates: Requirements 14.4**

- [ ]* 21.3 Write property test for result caching
  - **Property 57: Result caching**
  - **Validates: Requirements 16.1, 16.2**

- [ ]* 21.4 Write property test for processing time bound
  - **Property 58: Processing time bound**
  - **Validates: Requirements 16.3**

- [ ]* 21.5 Write property test for progress feedback
  - **Property 59: Progress feedback during processing**
  - **Validates: Requirements 16.5**

- [x] 22. Implement comprehensive error handling
  - Add try-catch blocks around all file operations
  - Implement fallback mechanisms (PDF parsing, grammar checking)
  - Ensure no stack traces are shown to users
  - Add specific error messages for all error types
  - Implement graceful degradation for component failures
  - Add error logging for debugging
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

- [ ]* 22.1 Write property test for validation error clarity
  - **Property 52: Validation error clarity**
  - **Validates: Requirements 15.1**

- [ ]* 22.2 Write property test for extraction fallback
  - **Property 53: Extraction fallback attempts**
  - **Validates: Requirements 15.2**

- [ ]* 22.3 Write property test for graceful degradation
  - **Property 54: Graceful component degradation**
  - **Validates: Requirements 15.3**

- [ ]* 22.4 Write property test for user-friendly errors
  - **Property 55: User-friendly error messages**
  - **Validates: Requirements 15.4**

- [ ]* 22.5 Write property test for model load error guidance
  - **Property 56: Model load error guidance**
  - **Validates: Requirements 15.5**

- [x] 23. Create data files and resources
  - Create data/skills_database.json with technical and soft skills
  - Create data/action_verbs.json with common action verbs
  - Create data/industry_keywords.json with industry-specific terms
  - Create data/common_locations.json for location detection
  - Add icons and assets to assets/ directory
  - _Requirements: 5.4, 6.1, 8.1_

- [x] 24. Create history tracking page
  - Create pages/2_📊_History.py
  - Implement analysis history storage in session state or database
  - Display list of past analyses with timestamps
  - Implement comparison between analyses
  - Add ability to re-analyze saved resumes
  - Show progress tracking over time
  - _Requirements: 2.3_

- [x] 25. Create resources page
  - Create pages/3_📚_Resources.py
  - Add resume writing tips and best practices
  - Add ATS optimization guidelines
  - Add links to helpful resources
  - Add downloadable resume templates
  - _Requirements: 1.1_

- [x] 26. Add custom styling and UI polish
  - Create assets/styles.css with custom CSS
  - Implement smooth animations and transitions
  - Add hover effects on interactive elements
  - Ensure responsive design for mobile and desktop
  - Add loading states with spinners
  - Implement consistent spacing and typography
  - _Requirements: 1.3_

- [ ] 27. Create comprehensive documentation
  - Write detailed README.md with setup instructions
  - Document all functions with docstrings
  - Create user guide for the application
  - Add inline code comments
  - Create troubleshooting guide
  - Document deployment process
  - _Requirements: 15.5_

- [ ] 28. Final checkpoint - Ensure all tests pass
  - Run all unit tests and verify they pass
  - Run all property-based tests and verify they pass
  - Run integration tests with real resume samples
  - Verify test coverage meets goals (80%+ for unit tests, 100% for properties)
  - Fix any failing tests
  - Ask the user if questions arise
  - _Requirements: All_
