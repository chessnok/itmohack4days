'use client';

import React from 'react';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { Message } from '../../lib/types';

interface ChatAreaProps {
    messages: Message[];
    isLoading: boolean;
    isStreaming: boolean;
    onSendMessage: (message: string) => void;
    onAbortStream?: () => void;
}

export function ChatArea({
    messages,
    isLoading,
    isStreaming,
    onSendMessage,
    onAbortStream
}: ChatAreaProps) {
    return (
        <div className="flex flex-col h-full">
            <MessageList
                messages={messages}
                isLoading={isLoading}
                isStreaming={isStreaming}
            />
            <ChatInput
                onSendMessage={onSendMessage}
                disabled={isLoading || isStreaming}
                isStreaming={isStreaming}
            />
        </div>
    );
}
