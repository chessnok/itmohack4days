import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { cookieUtils } from './cookies';
import {
    UserCreate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    SessionResponse,
    ChatRequest,
    ChatResponse,
    Message,
    ApiError,
} from './types';

class ApiClient {
    private client: AxiosInstance;

    constructor() {
        this.client = axios.create({
            baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        this.setupInterceptors();
    }

    private setupInterceptors() {
        // Request interceptor to add auth headers
        this.client.interceptors.request.use((config) => {
            // Use session token if available, otherwise user token
            const token = cookieUtils.getCurrentToken();
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        });

        // Response interceptor for error handling
        this.client.interceptors.response.use(
            (response) => response,
            (error) => {
                if (error.response?.status === 401) {
                    // Clear tokens on unauthorized
                    cookieUtils.clearTokens();
                }
                return Promise.reject(error);
            }
        );
    }

    // Token management
    setUserToken(token: string) {
        cookieUtils.setUserToken(token);
    }

    setSessionToken(token: string) {
        cookieUtils.setSessionToken(token);
    }

    clearTokens() {
        cookieUtils.clearTokens();
    }

    getCurrentToken(): string | null {
        return cookieUtils.getCurrentToken();
    }

    // Auth endpoints
    async register(userData: UserCreate): Promise<UserResponse> {
        const response: AxiosResponse<UserResponse> = await this.client.post(
            '/api/v1/auth/register',
            userData
        );
        return response.data;
    }

    async login(credentials: LoginRequest): Promise<TokenResponse> {
        const formData = new FormData();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);
        formData.append('grant_type', credentials.grant_type || 'password');

        const response: AxiosResponse<TokenResponse> = await this.client.post(
            '/api/v1/auth/login',
            formData,
            {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            }
        );
        return response.data;
    }

    // Session endpoints
    async createSession(): Promise<SessionResponse> {
        const response: AxiosResponse<SessionResponse> = await this.client.post(
            '/api/v1/auth/session'
        );
        return response.data;
    }

    async getSessions(): Promise<SessionResponse[]> {
        const response: AxiosResponse<SessionResponse[]> = await this.client.get(
            '/api/v1/auth/sessions'
        );
        return response.data;
    }

    async updateSessionName(sessionId: string, name: string): Promise<SessionResponse> {
        const formData = new FormData();
        formData.append('name', name);

        const response: AxiosResponse<SessionResponse> = await this.client.patch(
            `/api/v1/auth/session/${sessionId}/name`,
            formData,
            {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            }
        );
        return response.data;
    }

    async deleteSession(sessionId: string): Promise<void> {
        await this.client.delete(`/api/v1/auth/session/${sessionId}`);
    }

    // Chat endpoints
    async sendMessage(chatRequest: ChatRequest): Promise<ChatResponse> {
        const response: AxiosResponse<ChatResponse> = await this.client.post(
            '/api/v1/chatbot/chat',
            chatRequest
        );
        return response.data;
    }

    async getMessages(): Promise<ChatResponse> {
        const response: AxiosResponse<ChatResponse> = await this.client.get(
            '/api/v1/chatbot/messages'
        );
        return response.data;
    }

    async clearMessages(): Promise<{ message: string }> {
        const response: AxiosResponse<{ message: string }> = await this.client.delete(
            '/api/v1/chatbot/messages'
        );
        return response.data;
    }

    // Streaming chat
    async streamMessage(
        chatRequest: ChatRequest,
        onChunk: (chunk: string) => void,
        onComplete: () => void,
        onError: (error: string) => void
    ): Promise<void> {
        try {
            const response = await fetch(
                `${this.client.defaults.baseURL}/api/v1/chatbot/chat/stream`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: `Bearer ${this.getCurrentToken()}`,
                    },
                    body: JSON.stringify(chatRequest),
                }
            );

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body?.getReader();
            if (!reader) {
                throw new Error('No response body');
            }

            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            if (data.done) {
                                onComplete();
                            } else {
                                onChunk(data.content);
                            }
                        } catch (e) {
                            console.error('Error parsing SSE data:', e);
                        }
                    }
                }
            }
        } catch (error) {
            onError(error instanceof Error ? error.message : 'Unknown error');
        }
    }

    // Health check
    async healthCheck(): Promise<any> {
        const response = await this.client.get('/health');
        return response.data;
    }
}

export const apiClient = new ApiClient();
