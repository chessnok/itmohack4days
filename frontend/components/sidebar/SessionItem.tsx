'use client';

import React, { useState } from 'react';
import { Session } from '../../lib/types';
import { useSessions } from '../../hooks/useSessions';
import { Trash2, Edit2, Check, X } from 'lucide-react';

interface SessionItemProps {
    session: Session;
    isActive: boolean;
    onSelect: (session: Session) => void;
}

export function SessionItem({ session, isActive, onSelect }: SessionItemProps) {
    const { updateSessionName, deleteSession } = useSessions();
    const [isEditing, setIsEditing] = useState(false);
    const [editName, setEditName] = useState(session.name);

    const handleRename = async () => {
        if (editName.trim() && editName !== session.name) {
            const success = await updateSessionName(session.session_id, editName.trim());
            if (success) {
                setIsEditing(false);
            }
        } else {
            setIsEditing(false);
            setEditName(session.name);
        }
    };

    const handleDelete = async () => {
        if (confirm('Are you sure you want to delete this session?')) {
            await deleteSession(session.session_id);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleRename();
        } else if (e.key === 'Escape') {
            setIsEditing(false);
            setEditName(session.name);
        }
    };

    return (
        <div
            className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors ${isActive
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300'
                }`}
            onClick={() => !isEditing && onSelect(session)}
        >
            {isEditing ? (
                <div className="flex-1 flex items-center space-x-2">
                    <input
                        type="text"
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        onKeyDown={handleKeyPress}
                        className="flex-1 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        autoFocus
                    />
                    <button
                        onClick={handleRename}
                        className="p-1 text-green-600 hover:text-green-700"
                    >
                        <Check size={16} />
                    </button>
                    <button
                        onClick={() => {
                            setIsEditing(false);
                            setEditName(session.name);
                        }}
                        className="p-1 text-red-600 hover:text-red-700"
                    >
                        <X size={16} />
                    </button>
                </div>
            ) : (
                <>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">
                            {session.name || 'New Chat'}
                        </p>
                    </div>
                    <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                setIsEditing(true);
                            }}
                            className="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                        >
                            <Edit2 size={14} />
                        </button>
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                handleDelete();
                            }}
                            className="p-1 text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400"
                        >
                            <Trash2 size={14} />
                        </button>
                    </div>
                </>
            )}
        </div>
    );
}
