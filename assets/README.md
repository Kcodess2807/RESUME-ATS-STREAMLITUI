# Assets Directory

This directory contains static assets for the ATS Resume Scorer application.

## Contents

### Stylesheets
- `styles.css` - Custom CSS styles for the application including:
  - Color variables and themes
  - Score color coding (green/yellow/red)
  - Card and metric styles
  - Progress bar animations
  - Badge and tag styles
  - Alert components
  - Button styles
  - Responsive design adjustments

### Icons (Emoji-based)
The application uses emoji icons for visual indicators:
- 📄 Document/Resume
- 🎯 Target/Score
- ✅ Success/Validated
- ❌ Error/Unvalidated
- ⚠️ Warning
- 💡 Tip/Recommendation
- 🔴 Critical priority
- 🟡 Medium priority
- 🟢 Low priority/Success
- 📊 Analytics/Charts
- 🔒 Privacy/Security
- 📝 Grammar/Writing

### Future Assets
Additional assets can be added here:
- Custom logo images
- Favicon
- Background patterns
- Illustration graphics
- PDF report templates

## Usage

### CSS Styles
The CSS file can be loaded in Streamlit using:
```python
with open('assets/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
```

### Color Scheme
- Primary: #4F46E5 (Indigo)
- Success: #10B981 (Green)
- Warning: #F59E0B (Amber)
- Danger: #EF4444 (Red)
- Info: #3B82F6 (Blue)
