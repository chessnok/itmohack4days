'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { apiClient } from '../lib/api';
import { cookieUtils } from '../lib/cookies';
import { User, Session, LoginRequest, UserCreate } from '../lib/types';

interface AuthContextType {
    user: User | null;
    currentSession: Session | null;
    isLoading: boolean;
    login: (credentials: LoginRequest) => Promise<void>;
    register: (userData: UserCreate) => Promise<void>;
    logout: () => void;
    createSession: () => Promise<Session>;
    setCurrentSession: (session: Session | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [currentSession, setCurrentSession] = useState<Session | null>(null);
    const [isLoading, setIsLoading] = useState(false); // Start with false

    useEffect(() => {
        // Only run on client side
        if (typeof window === 'undefined') {
            setIsLoading(false);
            return;
        }

        // Check if user is already logged in via cookies
        const token = cookieUtils.getCurrentToken();
        if (token) {
            // Token exists, create a mock user object since we don't have user info endpoint
            // In a real app, you'd call an endpoint like /me to get user details
            setUser({ id: 1, email: 'user@example.com' }); // Mock user
            setIsLoading(false);
        } else {
            setUser(null);
            setIsLoading(false);
        }
    }, []);

    const login = async (credentials: LoginRequest) => {
        try {
            const response = await apiClient.login(credentials);
            apiClient.setUserToken(response.access_token);

            // Create a session immediately after login
            const session = await apiClient.createSession();
            apiClient.setSessionToken(session.token.access_token);
            setCurrentSession(session);

            // For now, we'll create a mock user object since the backend doesn't return user info on login
            // In a real app, you might want to store user info in the token or make another API call
            setUser({
                id: 1, // This would come from the backend
                email: credentials.username,
            });
        } catch (error) {
            throw error;
        }
    };

    const register = async (userData: UserCreate) => {
        try {
            const response = await apiClient.register(userData);
            apiClient.setUserToken(response.token.access_token);

            // Create a session immediately after registration
            const session = await apiClient.createSession();
            apiClient.setSessionToken(session.token.access_token);
            setCurrentSession(session);

            setUser({
                id: response.id,
                email: response.email,
            });
        } catch (error) {
            throw error;
        }
    };

    const logout = () => {
        cookieUtils.clearTokens();
        setUser(null);
        setCurrentSession(null);
    };

    const createSession = async (): Promise<Session> => {
        const session = await apiClient.createSession();
        apiClient.setSessionToken(session.token.access_token);
        setCurrentSession(session);
        return session;
    };

    const value: AuthContextType = {
        user,
        currentSession,
        isLoading,
        login,
        register,
        logout,
        createSession,
        setCurrentSession,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
