'use client';

import React, { useState, useEffect } from 'react';
import { apiClient } from '../lib/api';
import { Session } from '../lib/types';
import { useAuth } from '../context/AuthContext';

export function useSessions() {
    const { user, currentSession, setCurrentSession } = useAuth();
    const [sessions, setSessions] = useState<Session[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchSessions = async () => {
        if (!user) return;

        setIsLoading(true);
        setError(null);

        try {
            const sessionResponses = await apiClient.getSessions();
            const sessionList = sessionResponses.map(sessionResponse => ({
                session_id: sessionResponse.session_id,
                name: sessionResponse.name,
                token: sessionResponse.token,
            }));
            setSessions(sessionList);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to fetch sessions');
        } finally {
            setIsLoading(false);
        }
    };

    const createSession = async (): Promise<Session | null> => {
        try {
            const sessionResponse = await apiClient.createSession();
            const newSession: Session = {
                session_id: sessionResponse.session_id,
                name: sessionResponse.name,
                token: sessionResponse.token,
            };

            setSessions(prev => [...prev, newSession]);
            setCurrentSession(newSession);
            return newSession;
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to create session');
            return null;
        }
    };

    const updateSessionName = async (sessionId: string, name: string): Promise<boolean> => {
        try {
            const sessionResponse = await apiClient.updateSessionName(sessionId, name);

            setSessions(prev => prev.map(session =>
                session.session_id === sessionId
                    ? { ...session, name: sessionResponse.name }
                    : session
            ));

            // Update current session if it's the one being renamed
            if (currentSession?.session_id === sessionId) {
                setCurrentSession({ ...currentSession, name: sessionResponse.name });
            }

            return true;
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to update session name');
            return false;
        }
    };

    const deleteSession = async (sessionId: string): Promise<boolean> => {
        try {
            await apiClient.deleteSession(sessionId);

            setSessions(prev => prev.filter(session => session.session_id !== sessionId));

            // If we're deleting the current session, switch to another one or create a new one
            if (currentSession?.session_id === sessionId) {
                const remainingSessions = sessions.filter(session => session.session_id !== sessionId);
                if (remainingSessions.length > 0) {
                    setCurrentSession(remainingSessions[0]);
                } else {
                    // Create a new session if no sessions remain
                    const newSession = await createSession();
                    if (!newSession) {
                        setCurrentSession(null);
                    }
                }
            }

            return true;
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to delete session');
            return false;
        }
    };

    const switchToSession = (session: Session) => {
        setCurrentSession(session);
        apiClient.setSessionToken(session.token.access_token);
    };

    useEffect(() => {
        if (user) {
            fetchSessions();
        }
    }, [user]);

    return {
        sessions,
        isLoading,
        error,
        fetchSessions,
        createSession,
        updateSessionName,
        deleteSession,
        switchToSession,
    };
}
