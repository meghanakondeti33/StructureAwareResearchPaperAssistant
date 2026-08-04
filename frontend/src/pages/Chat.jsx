import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams, useLocation, useNavigate, Link } from 'react-router-dom';
import { askQuestion, getHistory } from '../services/chatApi';

const Chat = () => {
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();

  const documentId = searchParams.get('documentId') || location.state?.document?._id;
  const paperName = location.state?.document?.paperName || 'Research Paper';

  const [messages, setMessages] = useState([]);
  const [questionInput, setQuestionInput] = useState('');
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [asking, setAsking] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [expandedSources, setExpandedSources] = useState({});

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (!documentId) {
      setErrorMessage('No document selected. Please select a paper from the Dashboard.');
      setLoadingHistory(false);
      return;
    }

    const fetchChatHistory = async () => {
      try {
        const response = await getHistory(documentId);
        if (response.data && response.data.history) {
          const formattedHistory = [];
          response.data.history.forEach((chat) => {
            formattedHistory.push({
              id: `${chat._id}-q`,
              sender: 'user',
              text: chat.question,
              timestamp: chat.createdAt,
            });
            formattedHistory.push({
              id: `${chat._id}-a`,
              sender: 'ai',
              text: chat.answer,
              sources: chat.retrievedSections || [],
              timestamp: chat.createdAt,
            });
          });
          setMessages(formattedHistory);
        }
      } catch (err) {
        console.error('Failed to fetch chat history:', err);
        if (err.response?.status === 401) {
          navigate('/login');
        } else {
          setErrorMessage('Could not load conversation history.');
        }
      } finally {
        setLoadingHistory(false);
      }
    };

    fetchChatHistory();
  }, [documentId, navigate]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, asking]);

  const handleSendQuestion = async (e) => {
    e.preventDefault();
    const query = questionInput.trim();
    if (!query || asking || !documentId) return;

    const userMessageId = `user-${Date.now()}`;
    const userMsg = {
      id: userMessageId,
      sender: 'user',
      text: query,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setQuestionInput('');
    setAsking(true);
    setErrorMessage(null);

    try {
      const response = await askQuestion(documentId, query);
      if (response.data && response.data.answer) {
        const aiMsg = {
          id: `ai-${Date.now()}`,
          sender: 'ai',
          text: response.data.answer,
          sources: response.data.retrievedSections || [],
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, aiMsg]);
      }
    } catch (err) {
      console.error('Error asking question:', err);
      setErrorMessage(
        err.response?.data?.message || 'Failed to get answer from AI service. Please try again.'
      );
    } finally {
      setAsking(false);
    }
  };

  const toggleSourceExpand = (msgId) => {
    setExpandedSources((prev) => ({
      ...prev,
      [msgId]: !prev[msgId],
    }));
  };

  const formatSimilarityScore = (score) => {
    if (typeof score !== 'number') return null;
    const percentage = (score * 100).toFixed(1);
    return `${percentage}% Match`;
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      {/* Top Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link
              to="/dashboard"
              className="inline-flex items-center text-sm font-semibold text-brand-600 hover:text-brand-700 bg-brand-50 hover:bg-brand-100 px-3 py-1.5 rounded-lg transition-colors"
            >
              &larr; Back to Dashboard
            </Link>
            <div className="h-5 w-px bg-gray-300 hidden sm:block"></div>
            <div className="flex items-center space-x-2 truncate max-w-xs sm:max-w-md">
              <svg className="w-5 h-5 text-red-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
              </svg>
              <h1 className="text-base font-bold text-gray-900 truncate" title={paperName}>
                {paperName}
              </h1>
            </div>
          </div>
        </div>
      </header>

      {/* Main Chat Workspace */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 py-6 flex flex-col justify-between">
        {/* Error Alert */}
        {errorMessage && (
          <div className="mb-4 bg-rose-50 border border-rose-200 text-rose-800 px-4 py-3 rounded-lg flex items-center shadow-sm">
            <svg className="w-5 h-5 mr-2 text-rose-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span className="text-sm font-medium">{errorMessage}</span>
          </div>
        )}

        {/* Conversation Stream Container */}
        <div className="flex-1 bg-white border border-gray-200 rounded-2xl p-4 sm:p-6 shadow-sm overflow-y-auto min-h-[480px] max-h-[650px] space-y-6 mb-4">
          {loadingHistory ? (
            <div className="h-full flex items-center justify-center text-gray-400 py-20">
              <svg className="animate-spin h-6 w-6 mr-2 text-brand-600" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="text-sm">Loading conversation history...</span>
            </div>
          ) : messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center py-16 text-gray-400">
              <div className="w-14 h-14 rounded-2xl bg-brand-50 text-brand-600 flex items-center justify-center mb-3 shadow-inner">
                <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h3 className="text-base font-semibold text-gray-800 mb-1">Start Asking Questions</h3>
              <p className="text-xs text-gray-500 max-w-sm">
                Ask about methodology, findings, abstracts, or specific sections in <strong>{paperName}</strong>.
              </p>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                {/* Message Bubble */}
                <div
                  className={`max-w-[85%] rounded-2xl px-5 py-3.5 shadow-sm text-sm leading-relaxed ${
                    msg.sender === 'user'
                      ? 'bg-brand-600 text-white rounded-br-none font-medium'
                      : 'bg-gray-100 text-gray-900 border border-gray-200/80 rounded-bl-none'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.text}</p>
                </div>

                {/* Retrieved Sources Accordion for AI Messages */}
                {msg.sender === 'ai' && msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 max-w-[85%] w-full">
                    <button
                      onClick={() => toggleSourceExpand(msg.id)}
                      className="inline-flex items-center space-x-1.5 text-xs font-semibold text-brand-600 hover:text-brand-700 bg-brand-50 hover:bg-brand-100/80 px-3 py-1.5 rounded-lg border border-brand-200 transition-colors"
                    >
                      <svg
                        className={`w-3.5 h-3.5 transform transition-transform ${
                          expandedSources[msg.id] ? 'rotate-90' : ''
                        }`}
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                      </svg>
                      <span>
                        {expandedSources[msg.id] ? 'Hide' : 'View'} Retrieved Sources ({msg.sources.length})
                      </span>
                    </button>

                    {/* Expandable Source Cards */}
                    {expandedSources[msg.id] && (
                      <div className="mt-2 space-y-2.5 bg-gray-50 border border-gray-200 p-3 rounded-xl shadow-inner">
                        <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">
                          Source Sections & Similarity Scores:
                        </h4>
                        {msg.sources.map((src, idx) => (
                          <div
                            key={idx}
                            className="bg-white border border-gray-200 rounded-lg p-3 shadow-sm text-xs space-y-1.5"
                          >
                            <div className="flex items-center justify-between border-b border-gray-100 pb-1">
                              <span className="font-semibold text-brand-700 truncate max-w-[240px]">
                                📌 {src.sectionTitle || 'Section'}
                              </span>
                              <div className="flex items-center space-x-2">
                                <span className="bg-gray-100 text-gray-600 px-2 py-0.5 rounded font-mono text-[10px]">
                                  Page {src.pageNumber}
                                </span>
                                {src.score !== undefined && (
                                  <span className="bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded text-[10px]">
                                    {formatSimilarityScore(src.score) || `Score: ${src.score}`}
                                  </span>
                                )}
                              </div>
                            </div>
                            <p className="text-gray-600 italic bg-gray-50 p-2 rounded text-[11px] leading-relaxed border border-gray-100">
                              "{src.snippet}"
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          )}

          {/* Asking Loading Indicator */}
          {asking && (
            <div className="flex flex-col items-start">
              <div className="bg-gray-100 border border-gray-200 text-gray-500 rounded-2xl rounded-bl-none px-5 py-3.5 shadow-sm text-sm flex items-center space-x-3">
                <svg className="animate-spin h-4 w-4 text-brand-600" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span className="font-medium text-gray-600">Retrieving vector contexts & generating AI answer...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Question Input Form */}
        <form onSubmit={handleSendQuestion} className="relative">
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={questionInput}
              onChange={(e) => setQuestionInput(e.target.value)}
              placeholder="Ask a question about this research paper..."
              disabled={asking || !documentId}
              className="flex-1 bg-white border border-gray-300 text-gray-900 text-sm rounded-xl px-4 py-3.5 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 disabled:bg-gray-100 disabled:cursor-not-allowed shadow-sm transition-all"
            />
            <button
              type="submit"
              disabled={!questionInput.trim() || asking || !documentId}
              className={`px-6 py-3.5 rounded-xl font-semibold text-sm text-white shadow-sm transition-all flex items-center space-x-2 flex-shrink-0 ${
                !questionInput.trim() || asking || !documentId
                  ? 'bg-gray-300 cursor-not-allowed'
                  : 'bg-brand-600 hover:bg-brand-700 active:scale-[0.98]'
              }`}
            >
              <span>Ask AI</span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </button>
          </div>
        </form>
      </main>
    </div>
  );
};

export default Chat;
