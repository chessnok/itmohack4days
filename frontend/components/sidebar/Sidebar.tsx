'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Plus, Menu, X, LogOut, User } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useSessions } from '../../hooks/useSessions';
import { SessionList } from './SessionList';

interface SidebarProps {
    currentSession: any;
    onSessionSelect: (session: any) => void;
}

export function Sidebar({ currentSession, onSessionSelect }: SidebarProps) {
    const { user, logout } = useAuth();
    const { createSession } = useSessions();
    const [isCollapsed, setIsCollapsed] = useState(false);

    const handleNewSession = async () => {
        const newSession = await createSession();
        if (newSession) {
            onSessionSelect(newSession);
        }
    };

    return (
        <>
            {/* Mobile overlay */}
            {!isCollapsed && (
                <div
                    className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
                    onClick={() => setIsCollapsed(true)}
                />
            )}

            {/* Sidebar */}
            <div className={`
        fixed lg:static inset-y-0 left-0 z-50 w-80 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700
        transform transition-transform duration-200 ease-in-out
        ${isCollapsed ? '-translate-x-full lg:translate-x-0' : 'translate-x-0'}
      `}>
                <div className="flex flex-col h-full">
                    {/* Header */}
                    <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                        <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
                            Chat Assistant
                        </h1>
                        <div className="flex items-center space-x-2">
                            <button
                                onClick={handleNewSession}
                                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                                title="New chat"
                            >
                                <Plus size={20} />
                            </button>
                            <button
                                onClick={() => setIsCollapsed(true)}
                                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors lg:hidden"
                            >
                                <X size={20} />
                            </button>
                        </div>
                    </div>

                    {/* Sessions */}
                    <div className="flex-1 overflow-y-auto p-4">
                        <SessionList
                            currentSession={currentSession}
                            onSessionSelect={onSessionSelect}
                        />
                    </div>

                    {/* User info and logout */}
                    <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                        <div className="flex items-center space-x-3 mb-3">
                            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                                <User size={20} className="text-blue-600 dark:text-blue-400" />
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                                    {user?.email}
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={logout}
                            className="w-full flex items-center space-x-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                        >
                            <LogOut size={16} />
                            <span>Sign out</span>
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile menu button */}
            <button
                onClick={() => setIsCollapsed(false)}
                className="fixed top-4 left-4 z-40 p-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg lg:hidden"
            >
                <Menu size={20} className="text-gray-600 dark:text-gray-400" />
            </button>
        </>
    );
}
