'use client';

import { useState, useCallback, useRef } from 'react';
import { apiClient } from '../lib/api';
import { Message, ChatRequest } from '../lib/types';

export function useChat(sessionId: string | null) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isStreaming, setIsStreaming] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const abortControllerRef = useRef<AbortController | null>(null);

    const loadMessages = useCallback(async () => {
        if (!sessionId) return;

        setIsLoading(true);
        setError(null);

        try {
            const response = await apiClient.getMessages();
            setMessages(response.messages);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load messages');
        } finally {
            setIsLoading(false);
        }
    }, [sessionId]);

    const sendMessage = useCallback(async (content: string) => {
        if (!sessionId || !content.trim()) return;

        const userMessage: Message = {
            role: 'user',
            content: content.trim(),
        };

        const assistantMessage: Message = {
            role: 'assistant',
            content: '',
        };

        // Add user message immediately
        setMessages(prev => [...prev, userMessage]);

        // Add empty assistant message for streaming
        setMessages(prev => [...prev, assistantMessage]);

        setIsStreaming(true);
        setError(null);

        const chatRequest: ChatRequest = {
            messages: [...messages, userMessage],
        };

        try {
            await apiClient.streamMessage(
                chatRequest,
                (chunk: string) => {
                    setMessages(prev => {
                        const newMessages = [...prev];
                        const lastMessage = newMessages[newMessages.length - 1];
                        if (lastMessage && lastMessage.role === 'assistant') {
                            lastMessage.content += chunk;
                        }
                        return newMessages;
                    });
                },
                () => {
                    setIsStreaming(false);
                },
                (error: string) => {
                    setError(error);
                    setIsStreaming(false);
                    // Remove the empty assistant message on error
                    setMessages(prev => prev.slice(0, -1));
                }
            );
        } catch (err: any) {
            setError(err.message || 'Failed to send message');
            setIsStreaming(false);
            // Remove the empty assistant message on error
            setMessages(prev => prev.slice(0, -1));
        }
    }, [sessionId, messages]);

    const clearMessages = useCallback(async () => {
        if (!sessionId) return;

        try {
            await apiClient.clearMessages();
            setMessages([]);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to clear messages');
        }
    }, [sessionId]);

    const abortStream = useCallback(() => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            abortControllerRef.current = null;
        }
        setIsStreaming(false);
    }, []);

    return {
        messages,
        isLoading,
        isStreaming,
        error,
        sendMessage,
        loadMessages,
        clearMessages,
        abortStream,
    };
}
