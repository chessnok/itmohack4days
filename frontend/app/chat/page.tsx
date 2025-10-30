'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../context/AuthContext';
import { useChat } from '../../hooks/useChat';
import { Sidebar } from '../../components/sidebar/Sidebar';
import { ChatArea } from '../../components/chat/ChatArea';

export default function ChatPage() {
    const { user, currentSession, isLoading: authLoading, setCurrentSession } = useAuth();
    const { messages, isLoading, isStreaming, sendMessage, loadMessages, abortStream } = useChat(
        currentSession?.session_id || null
    );
    const router = useRouter();

    // Redirect to login if not authenticated
    useEffect(() => {
        if (!authLoading && !user) {
            router.push('/login');
        }
    }, [user, authLoading, router]);

    // Load messages when session changes
    useEffect(() => {
        if (currentSession) {
            loadMessages();
        }
    }, [currentSession, loadMessages]);

    const handleSessionSelect = (session: any) => {
        setCurrentSession(session);
    };

    if (authLoading) {
        return (
            <div className="h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (!user) {
        return null; // Will redirect to login
    }

    return (
        <div className="h-screen flex bg-white dark:bg-gray-900">
            <Sidebar
                currentSession={currentSession}
                onSessionSelect={handleSessionSelect}
            />
            <div className="flex-1 flex flex-col lg:ml-0">
                <ChatArea
                    messages={messages}
                    isLoading={isLoading}
                    isStreaming={isStreaming}
                    onSendMessage={sendMessage}
                    onAbortStream={abortStream}
                />
            </div>
        </div>
    );
}
