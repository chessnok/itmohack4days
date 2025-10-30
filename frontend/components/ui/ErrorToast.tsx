'use client';

import React from 'react';
import { AlertCircle, X } from 'lucide-react';

interface ErrorToastProps {
    message: string;
    onClose: () => void;
}

export function ErrorToast({ message, onClose }: ErrorToastProps) {
    return (
        <div className="fixed top-4 right-4 z-50 max-w-sm w-full bg-red-50 border border-red-200 rounded-lg shadow-lg">
            <div className="p-4">
                <div className="flex items-start">
                    <div className="flex-shrink-0">
                        <AlertCircle className="h-5 w-5 text-red-400" />
                    </div>
                    <div className="ml-3 flex-1">
                        <p className="text-sm font-medium text-red-800">{message}</p>
                    </div>
                    <div className="ml-4 flex-shrink-0">
                        <button
                            onClick={onClose}
                            className="inline-flex text-red-400 hover:text-red-600 focus:outline-none"
                        >
                            <X className="h-4 w-4" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
