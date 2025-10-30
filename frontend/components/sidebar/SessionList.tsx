'use client';

import React from 'react';
import { Session } from '../../lib/types';
import { useSessions } from '../../hooks/useSessions';
import { SessionItem } from './SessionItem';

interface SessionListProps {
    currentSession: Session | null;
    onSessionSelect: (session: Session) => void;
}

export function SessionList({ currentSession, onSessionSelect }: SessionListProps) {
    const { sessions, isLoading, error } = useSessions();

    if (isLoading) {
        return (
            <div className="flex items-center justify-center p-4">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4 text-red-600 dark:text-red-400 text-sm">
                Error loading sessions: {error}
            </div>
        );
    }

    if (sessions.length === 0) {
        return (
            <div className="p-4 text-gray-500 dark:text-gray-400 text-sm text-center">
                No sessions yet. Create your first chat!
            </div>
        );
    }

    return (
        <div className="space-y-1">
            {sessions.map((session) => (
                <SessionItem
                    key={session.session_id}
                    session={session}
                    isActive={currentSession?.session_id === session.session_id}
                    onSelect={onSessionSelect}
                />
            ))}
        </div>
    );
}
