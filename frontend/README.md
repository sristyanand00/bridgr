# Bridgr

**Bridge between who you are and who you want to become**

AI Career Intelligence Platform - Modern React application with component-based architecture.

## 🏗️ Project Structure

```
frontend/
├── public/                 # Static assets
│   └── index.html         # HTML template
├── src/
│   ├── components/        # Reusable components
│   │   ├── ui/           # UI components (Button, Card, Chip, etc.)
│   │   ├── layout/       # Layout components (Sidebar, Topbar, Cursor)
│   │   └── forms/        # Form components (Quiz, AuthModal, RoleGuidance)
│   ├── pages/            # Page components (Dashboard, Resume, Chat, etc.)
│   ├── hooks/            # Custom React hooks
│   ├── styles/           # CSS and styling
│   ├── constants/         # Application constants
│   ├── types/            # Type definitions
│   ├── utils/            # Utility functions
│   ├── App.jsx           # Main application component
│   └── index.js          # Application entry point
├── package.json
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Installation
```bash
cd frontend
npm install
```

### Development
```bash
npm start
```

### Production Build
```bash
npm run build
```

## 🎨 Features

### Component Architecture
- **UI Components**: Reusable, styled components with consistent design system
- **Layout Components**: Application layout and navigation
- **Form Components**: Interactive forms with validation
- **Page Components**: Full-page components for different sections

### Key Features
- **Resume Analysis**: AI-powered resume scoring and skill gap analysis
- **Career Coach**: Personalized AI chat based on user profile
- **Market Pulse**: Real-time job market insights and salary data
- **Learning Roadmap**: Personalized skill development plans
- **Mock Interviews**: Practice interview sessions with feedback

### Design System
- **Custom Cursor**: Animated cursor with reduced motion support
- **Glass Morphism**: Modern glass-like UI elements
- **Dark Theme**: Eye-friendly dark color scheme
- **Responsive Design**: Mobile-first responsive layout
- **Animations**: Smooth transitions and micro-interactions

## 🧩 Components

### UI Components
- `Button` - Primary, secondary, and size variants
- `Card` - Reusable card container
- `Chip` - Status and category tags
- `Icon` - SVG icon system
- `Input` - Form input with styling
- `ProgressBar` - Animated progress bars
- `Ring` - Circular progress indicator
- `Counter` - Animated number counter

### Layout Components
- `Sidebar` - Navigation sidebar
- `Topbar` - Page header with actions
- `Cursor` - Custom animated cursor

### Form Components
- `Quiz` - Multi-step onboarding quiz
- `AuthModal` - Authentication modal
- `RoleGuidance` - Role selection guidance

## 🎯 Pages

- **Dashboard**: Overview with metrics and progress tracking
- **Resume**: Resume upload and analysis
- **Chat**: AI career coach interface
- **Roadmap**: Personalized learning plan
- **Market**: Job market insights
- **Interview**: Mock interview simulator
- **Pricing**: Subscription plans
- **Settings**: User preferences and profile

## 🔧 Hooks

- `useCursor` - Custom cursor animation logic
- `useTimer` - Countdown timer with controls

## 📦 Dependencies

### Core
- React 18+ - UI library
- React DOM - DOM rendering

### Development
- Vite - Build tool and dev server
- React Scripts - Alternative build system

## 🎨 Styling

The application uses a custom CSS design system with:
- CSS custom properties for theming
- Component-based CSS classes
- Responsive design patterns
- Animation keyframes
- Glass morphism effects

## 🔐 Features

- **Google OAuth Integration** - Secure authentication
- **Progress Tracking** - Score improvement over time
- **Personalized Recommendations** - AI-driven insights
- **Real-time Market Data** - Current job market trends
- **Interactive Learning Paths** - Step-by-step guidance

## 🌱 Environment Variables

Create a `.env.local` file in the root:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
```

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🚀 Deployment

The application can be deployed to any static hosting service:

```bash
npm run build
# Deploy the build/ folder
```

## 🤝 Contributing

1. Follow the established component structure
2. Use the existing design system
3. Maintain responsive design principles
4. Test across different screen sizes
5. Follow React best practices

## 📄 License

MIT License - see LICENSE file for details.
