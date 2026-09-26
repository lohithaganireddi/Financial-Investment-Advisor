import React, { useState, useEffect, useRef } from 'react';
import {
  MessageSquare,
  Send,
  Sparkles,
  Bot,
  User,
  HelpCircle,
  Cpu,
  RefreshCw
} from 'lucide-react';

export default function LLMChatAssistant({ analysisData }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [provider, setProvider] = useState(null);

  const chatBottomRef = useRef(null);

  const assetName = analysisData?.asset || analysisData?.market_data?.symbol || 'Asset';

  const suggestedPrompts = [
    `Explain the risk breakdown for ${assetName}`,
    `What are the key bullish catalysts for ${assetName}?`,
    `How should a conservative investor approach ${assetName}?`,
    `Summarize recent news sentiment for ${assetName}`,
  ];

  useEffect(() => {
    // Reset conversation when a new asset analysis is loaded
    setMessages([]);
    setInput('');
    setProvider(null);
  }, [analysisData?.asset, analysisData?.saved_analysis_id]);

  useEffect(() => {
    if (chatBottomRef.current) {
      chatBottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, loading]);

  if (!analysisData || analysisData.success === false) {
    return null;
  }

  const handleSendMessage = async (textToSend) => {
    const queryText = (textToSend || input).trim();
    if (!queryText || loading) return;

    const userMsg = { role: 'user', content: queryText };
    const updatedMessages = [...messages, userMsg];

    setMessages(updatedMessages);
    if (!textToSend) setInput('');
    setLoading(true);

    try {
      const resp = await fetch('/api/llm/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: updatedMessages,
          analysis_context: analysisData,
          provider: 'auto',
        }),
      });

      if (resp.ok) {
        const data = await resp.json();
        if (data.success && data.reply) {
          setMessages((prev) => [...prev, { role: 'assistant', content: data.reply }]);
          if (data.provider) setProvider(data.provider);
        }
      }
    } catch (err) {
      console.warn('LLM Chat request failed:', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Unable to reach LLM reasoning assistant. Please verify backend service connection.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setInput('');
  };

  return (
    <div
      className="card"
      style={{
        background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%)',
        border: '1px solid rgba(59, 130, 246, 0.35)',
        marginTop: '1.25rem',
      }}
    >
      {/* Card Header */}
      <div className="card-title" style={{ justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <MessageSquare size={20} color="#3b82f6" />
          Interactive LLM Financial Assistant & Q&A
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {provider && (
            <span
              className="status-badge"
              style={{
                backgroundColor: 'rgba(59, 130, 246, 0.15)',
                color: '#60a5fa',
                border: '1px solid rgba(59, 130, 246, 0.3)',
                fontSize: '0.75rem',
              }}
            >
              <Cpu size={12} /> {provider === 'offline_fallback' ? 'Hybrid Fallback LLM' : `${provider.toUpperCase()} AI`}
            </span>
          )}

          {messages.length > 0 && (
            <button
              onClick={handleClearChat}
              className="tab-btn"
              style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}
              title="Clear conversation history"
            >
              <RefreshCw size={12} /> Reset Chat
            </button>
          )}
        </div>
      </div>

      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
        Ask conversational follow-up questions about <strong>{assetName}</strong>. Responses are dynamically grounded in the active agent analysis output.
      </p>

      {/* Suggested Follow-up Prompt Chips */}
      {messages.length === 0 && (
        <div style={{ marginBottom: '1.25rem' }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: 4 }}>
            <HelpCircle size={13} color="#3b82f6" /> Suggested Analysis Inquiries
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {suggestedPrompts.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(prompt)}
                disabled={loading}
                style={{
                  background: 'rgba(59, 130, 246, 0.1)',
                  border: '1px solid rgba(59, 130, 246, 0.3)',
                  color: '#93c5fd',
                  borderRadius: '20px',
                  padding: '0.4rem 0.8rem',
                  fontSize: '0.8rem',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  textAlign: 'left',
                }}
              >
                + {prompt}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Chat Conversation Thread Box */}
      {messages.length > 0 && (
        <div
          style={{
            maxHeight: '320px',
            overflowY: 'auto',
            background: 'rgba(11, 15, 25, 0.6)',
            borderRadius: '10px',
            padding: '1rem',
            border: '1px solid var(--border-color)',
            marginBottom: '1rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.85rem',
          }}
        >
          {messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
              }}
            >
              <div
                style={{
                  maxWidth: '85%',
                  background: msg.role === 'user' ? 'rgba(59, 130, 246, 0.2)' : 'rgba(30, 41, 59, 0.8)',
                  border: `1px solid ${msg.role === 'user' ? 'rgba(59, 130, 246, 0.4)' : 'rgba(148, 163, 184, 0.2)'}`,
                  borderRadius: msg.role === 'user' ? '14px 14px 2px 14px' : '14px 14px 14px 2px',
                  padding: '0.75rem 1rem',
                  color: '#f8fafc',
                  fontSize: '0.88rem',
                  lineHeight: '1.5',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.72rem', fontWeight: 700, color: msg.role === 'user' ? '#60a5fa' : '#a855f7', marginBottom: 4 }}>
                  {msg.role === 'user' ? (
                    <>
                      <User size={12} /> You
                    </>
                  ) : (
                    <>
                      <Bot size={12} /> Financial Assistant
                    </>
                  )}
                </div>
                <div>{msg.content}</div>
              </div>
            </div>
          ))}

          {loading && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-muted)', fontSize: '0.82rem', padding: '0.3rem 0' }}>
              <div className="spinner" style={{ width: '16px', height: '16px' }}></div>
              <span>Assistant reasoning...</span>
            </div>
          )}

          <div ref={chatBottomRef} />
        </div>
      )}

      {/* Input Message Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSendMessage();
        }}
        style={{ display: 'flex', gap: '0.6rem' }}
      >
        <input
          type="text"
          className="form-input"
          placeholder={`Ask a question about ${assetName} (e.g. risk factors, catalysts)...`}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          style={{ flex: 1, padding: '0.65rem 0.85rem', fontSize: '0.88rem' }}
        />

        <button
          type="submit"
          className="btn-primary"
          disabled={loading || !input.trim()}
          style={{ padding: '0.65rem 1rem', display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.88rem' }}
        >
          <Send size={14} /> Send
        </button>
      </form>
    </div>
  );
}
