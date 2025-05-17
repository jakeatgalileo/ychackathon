"use client"

import React, { useState, useRef, useEffect } from 'react';
import { Textarea } from './ui/textarea';
import { Button } from './ui/button';

type Message = {
  role: 'user' | 'assistant';
  content: string;
  avatar?: string;
};

// API client for the backend
const api = {
  chat: async (messages: Message[]): Promise<string> => {
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ messages }),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`API error: ${response.status} - ${errorData.detail || 'Unknown error'}`);
      }
      
      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('Error calling chat API:', error);
      throw error;
    }
  }
};

export function ChatComponent() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'user',
      content: 'this is a test message',
      avatar: 'JK',
    },
    {
      role: 'assistant',
      content: "Hello! Thanks for your test message. I'm Claude, and I'm here to help you with a wide range of tasks",
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom of messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      avatar: 'JK',
    };

    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    const userInput = input;
    setInput('');
    setIsLoading(true);

    try {
      // Call the backend API
      const allMessages = [...messages, userMessage];
      const response = await api.chat(allMessages);
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: response,
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error communicating with backend:', error);
      // Add error message
      const errorMessage: Message = {
        role: 'assistant',
        content: "I'm sorry, I encountered an error processing your request. Please try again later.",
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Auto-resize the textarea
  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`;
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      <div className="flex-1 overflow-y-auto p-4 pb-32">
        {messages.map((message, index) => (
          <div key={index} className="mb-6">
            {message.role === 'user' ? (
              <div className="flex items-start">
                <div className="bg-gray-100 rounded-full h-8 w-8 flex items-center justify-center text-sm font-medium mr-2">
                  {message.avatar}
                </div>
                <div className="bg-gray-100 rounded-lg p-3 max-w-[85%]">
                  <p>{message.content}</p>
                </div>
              </div>
            ) : (
              <div className="ml-10">
                <p>{message.content}</p>
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="ml-10 flex items-center">
            <div className="text-orange-400">
              <LoadingSpinner className="h-6 w-6" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="fixed bottom-0 left-0 right-0 bg-white py-4">
        <div className="max-w-4xl mx-auto px-4">
          <form onSubmit={handleSubmit}>
            <div className="relative flex items-center bg-gray-50 rounded-lg border border-gray-200">
              <Textarea
                value={input}
                onChange={handleTextareaChange}
                placeholder="Reply to Claude..."
                className="resize-none overflow-hidden pr-16 py-3 px-4 bg-transparent border-0 focus-visible:ring-0 focus-visible:ring-offset-0 min-h-[44px] max-h-[200px]"
                rows={1}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
              />
              <div className="absolute right-3 flex items-center space-x-2">
                <Button 
                  type="button" 
                  size="icon" 
                  variant="ghost" 
                  className="h-8 w-8 rounded-full text-gray-500 hover:text-gray-700"
                >
                  <PlusIcon className="h-5 w-5" />
                </Button>
                <Button
                  type="submit"
                  size="icon"
                  variant="ghost"
                  className="h-8 w-8 rounded-full text-gray-500 hover:text-gray-700"
                  disabled={!input.trim() || isLoading}
                >
                  <SendIcon className="h-5 w-5" />
                </Button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

// Simple icons
const PlusIcon = ({ className = "" }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M12 5v14M5 12h14" />
  </svg>
);

const SendIcon = ({ className = "" }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="m22 2-7 20-4-9-9-4Z" />
    <path d="M22 2 11 13" />
  </svg>
);

const LoadingSpinner = ({ className = "" }: { className?: string }) => (
  <svg className={`animate-spin ${className}`} viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
  </svg>
);
