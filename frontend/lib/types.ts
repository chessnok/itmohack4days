export interface User {
    id: number;
    email: string;
}

export interface Token {
    access_token: string;
    token_type: string;
    expires_at: string;
}

export interface Session {
    session_id: string;
    name: string;
    token: Token;
}

export interface Message {
    role: "user" | "assistant" | "system";
    content: string;
}

export interface ChatRequest {
    messages: Message[];
}

export interface ChatResponse {
    messages: Message[];
}

export interface StreamResponse {
    content: string;
    done: boolean;
}

export interface UserCreate {
    email: string;
    password: string;
}

export interface UserResponse {
    id: number;
    email: string;
    token: Token;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
    expires_at: string;
}

export interface SessionResponse {
    session_id: string;
    name: string;
    token: Token;
}

export interface LoginRequest {
    username: string;
    password: string;
    grant_type?: string;
}

export interface ApiError {
    detail: string;
    errors?: Array<{
        field: string;
        message: string;
    }>;
}
