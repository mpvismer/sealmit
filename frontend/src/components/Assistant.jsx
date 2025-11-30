import React, { useState } from 'react';
import './Assistant.css';

function Assistant() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    const toggleOpen = () => setIsOpen(!isOpen);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = { role: 'user', content: input };
        setMessages([...messages, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const res = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: input, history: messages })
            });

            const data = await res.json();
            setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
        } catch (err) {
            console.error('Error chatting with AI:', err);
            setMessages(prev => [...prev, { role: 'assistant', content: 'Error: Could not reach AI.' }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={`assistant-container ${isOpen ? 'open' : ''}`}>
            <button className="assistant-toggle" onClick={toggleOpen}>
                {isOpen ? 'Close AI' : 'AI Assistant'}
            </button>

            {isOpen && (
                <div className="assistant-chat">
                    <div className="messages">
                        {messages.map((msg, idx) => (
                            <div key={idx} className={`message ${msg.role}`}>
                                {msg.content}
                            </div>
                        ))}
                        {loading && <div className="message assistant">Thinking...</div>}
                    </div>
                    <form onSubmit={handleSubmit} className="chat-input-form">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask AI..."
                        />
                        <button type="submit">Send</button>
                    </form>
                </div>
            )}
        </div>
    );
}

export default Assistant;
