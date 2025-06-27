# SkillSnap - Voice Challenge Platform

A modern voice challenge platform for hiring, built with vanilla HTML, CSS, and JavaScript.

## 📁 File Structure

```
SkillMap-Main/
├── index.html                 # Main HTML file with all page structures
├── README.md                  # This file
├── styles/
│   ├── main.css              # Global styles, typography, and layout
│   ├── components.css        # Component-specific styles (cards, buttons, forms)
│   └── responsive.css        # Recruiter dashboard and responsive styles
└── js/
    ├── data.js               # Mock data for challenges and candidates
    ├── utils.js              # Utility functions and application state
    ├── components.js         # Component rendering functions
    └── app.js                # Main application logic and event handlers
```

## 🚀 Getting Started

1. **Clone or download** this repository
2. **Open `index.html`** in a modern web browser
3. **Start exploring** the application:
   - Click "I'm a Candidate" to experience the candidate flow
   - Click "I'm a Recruiter" to access the recruiter dashboard

## ✨ Features

### For Candidates
- 📝 Personal information form
- 🎯 Role-specific voice challenges
- 🎤 Voice recording interface with timer
- 📊 Personal dashboard with challenge history
- 📈 Performance scoring and analytics

### For Recruiters
- 👥 Candidate management dashboard
- 🔍 Search and filter candidates
- 📊 Detailed scoring breakdown
- 🎧 Audio playback functionality
- 📅 Interview scheduling
- 📈 Analytics and reporting

## 🛠️ Technology Stack

- **HTML5** - Semantic markup and structure
- **CSS3** - Modern styling with Flexbox and Grid
- **Vanilla JavaScript** - Pure JavaScript without frameworks
- **Lucide Icons** - Beautiful, consistent iconography

## 📱 Responsive Design

The application is fully responsive and works on:
- 🖥️ Desktop computers
- 📱 Mobile phones
- 📟 Tablets

## 🔧 Development

### File Organization

- **`index.html`** - Contains all page structures in a single-page application format
- **`styles/`** - Separated CSS for maintainability:
  - `main.css` - Global styles and utilities
  - `components.css` - Reusable component styles
  - `responsive.css` - Dashboard and responsive layouts
- **`js/`** - Modular JavaScript:
  - `data.js` - All mock data and constants
  - `utils.js` - Helper functions and state management
  - `components.js` - DOM manipulation and rendering
  - `app.js` - Event handlers and application flow

### Key Features of the Architecture

1. **No Build Process** - Direct browser compatibility
2. **Modular CSS** - Organized by purpose and component
3. **Separation of Concerns** - Data, utilities, components, and app logic
4. **State Management** - Simple vanilla JavaScript state
5. **Responsive Design** - Mobile-first approach

## 🎨 Design System

### Colors
- **Primary Blue**: #2563eb
- **Success Green**: #16a34a  
- **Warning Yellow**: #ca8a04
- **Danger Red**: #dc2626
- **Purple**: #9333ea

### Typography
- **Font Family**: System fonts (Apple/Roboto/Segoe UI)
- **Weights**: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)

## 📊 Mock Data

The application includes realistic mock data for:
- **20 voice challenges** across multiple domains:
  - **Non-Technical Roles**: Sales, Support, Tech Support, Teaching
  - **Software Development**: JavaScript, Python, Java, C++, C#, PHP, Ruby, Go, Swift, Kotlin, Rust, TypeScript
  - **Engineering Roles**: Full Stack, DevOps, Mobile Development, Data Engineering
- **14 sample candidates** with complete scoring across different technical roles
- Challenge history and performance metrics for software developers

## 🔮 Future Enhancements

- Real voice recording functionality
- Backend API integration
- User authentication
- Advanced analytics
- Bulk operations
- Export functionality
- Email notifications

## 🤝 Contributing

This is a demonstration project. For production use, consider:
- Adding proper error handling
- Implementing real audio recording
- Adding data persistence
- Creating a proper backend API
- Adding automated testing

## 📄 License

This project is for demonstration purposes. Feel free to use and modify as needed. # SkillMap-Main
