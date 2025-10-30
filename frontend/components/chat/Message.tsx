'use client';

import React from 'react';
import { Message } from '../../lib/types';

interface MessageProps {
    message: Message;
}

export function MessageComponent({ message }: MessageProps) {
    const isUser = message.role === 'user';
    const isAssistant = message.role === 'assistant';

    return (
        <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
            <div
                className={`max-w-[80%] px-4 py-2 rounded-lg ${isUser
                        ? 'bg-blue-600 text-white'
                        : isAssistant
                            ? 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
                            : 'bg-yellow-100 dark:bg-yellow-900 text-yellow-900 dark:text-yellow-100'
                    }`}
            >
                <div className="text-sm whitespace-pre-wrap break-words">
                    {message.content}
                </div>
            </div>
        </div>
    );
}
