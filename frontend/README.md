# Frontend - Chat Assistant

A modern Next.js frontend for the Chat Assistant application with authentication, session management, and real-time streaming chat.

## Features

- **Authentication**: User registration and login with password validation
- **Session Management**: Create, rename, delete, and switch between chat sessions
- **Real-time Chat**: Streaming responses with Server-Sent Events (SSE)
- **Responsive Design**: Mobile-friendly sidebar and chat interface
- **Dark Mode**: Built-in dark mode support
- **Error Handling**: User-friendly error messages and loading states

## Tech Stack

- **Next.js 16** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Hook Form** - Form handling
- **Zod** - Schema validation
- **Axios** - HTTP client
- **Lucide React** - Icons

## Project Structure

```
frontend/
├── app/
│   ├── (auth)/           # Authentication pages
│   │   ├── login/
│   │   └── register/
│   ├── (chat)/           # Chat interface
│   │   └── page.tsx
│   ├── layout.tsx        # Root layout with AuthProvider
│   └── page.tsx          # Home page with redirects
├── components/
│   ├── auth/             # Authentication components
│   ├── chat/             # Chat interface components
│   ├── sidebar/          # Session management components
│   └── ui/               # Shared UI components
├── context/
│   └── AuthContext.tsx   # Authentication state management
├── hooks/
│   ├── useAuth.ts        # Authentication hook
│   ├── useChat.ts        # Chat functionality hook
│   └── useSessions.ts    # Session management hook
├── lib/
│   ├── api.ts           # API client
│   ├── types.ts         # TypeScript type definitions
│   └── utils.ts         # Utility functions
└── .env.local           # Environment configuration
```

## Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment**:
   Create `.env.local` with:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

## API Integration

The frontend integrates with the FastAPI backend through the following endpoints:

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login (OAuth2 password flow)
- `POST /api/v1/auth/session` - Create new chat session
- `GET /api/v1/auth/sessions` - Get user sessions
- `PATCH /api/v1/auth/session/{id}/name` - Update session name
- `DELETE /api/v1/auth/session/{id}` - Delete session

### Chat
- `POST /api/v1/chatbot/chat` - Send message (non-streaming)
- `POST /api/v1/chatbot/chat/stream` - Send message (streaming SSE)
- `GET /api/v1/chatbot/messages` - Get session messages
- `DELETE /api/v1/chatbot/messages` - Clear chat history

## Key Features

### Authentication Flow
1. User registers/logs in with email and password
2. JWT token is stored in localStorage
3. Session is automatically created after login
4. Session token is used for chat operations

### Session Management
- Sidebar displays all user sessions
- Click to switch between sessions
- Rename sessions inline
- Delete sessions with confirmation
- Create new sessions with the + button

### Streaming Chat
- Real-time message streaming using Server-Sent Events
- Typing indicators during streaming
- Abort streaming functionality
- Auto-scroll to latest messages

### Responsive Design
- Mobile-friendly sidebar that collapses on small screens
- Touch-friendly interface elements
- Dark mode support throughout

## Development Notes

- **Node.js Version**: Requires Node.js >=20.9.0 for Next.js 16
- **TypeScript**: Strict type checking enabled
- **ESLint**: Code quality and consistency
- **Tailwind**: Utility-first CSS framework
- **Client-side**: All components are client-side rendered for interactivity

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API base URL (default: http://localhost:8000)

## Browser Support

- Modern browsers with ES2020+ support
- Fetch API support for HTTP requests
- Server-Sent Events support for streaming