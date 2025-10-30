'use client';

import React, { useEffect, useRef } from 'react';
import { Message } from '../../lib/types';
import { MessageComponent } from './Message';

interface MessageListProps {
    messages: Message[];
    isLoading?: boolean;
    isStreaming?: boolean;
}

export function MessageList({ messages, isLoading, isStreaming }: MessageListProps) {
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isStreaming]);

    if (messages.length === 0 && !isLoading) {
        return (
            <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                    <div className="text-gray-400 dark:text-gray-600 mb-4">
                        <svg
                            className="mx-auto h-12 w-12"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={1}
                                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                            />
                        </svg>
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                        Start a conversation
                    </h3>
                    <p className="text-gray-500 dark:text-gray-400">
                        Send a message to begin chatting with the assistant.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-4">
                {messages.map((message, index) => (
                    <MessageComponent key={index} message={message} />
                ))}

                {isStreaming && (
                    <div className="flex justify-start mb-4">
                        <div className="bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-4 py-2 rounded-lg">
                            <div className="flex items-center space-x-2">
                                <div className="animate-pulse">●</div>
                                <div className="animate-pulse">●</div>
                                <div className="animate-pulse">●</div>
                            </div>
                        </div>
                    </div>
                )}

                {isLoading && (
                    <div className="flex justify-center mb-4">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    </div>
                )}
            </div>
            <div ref={messagesEndRef} />
        </div>
    );
}
