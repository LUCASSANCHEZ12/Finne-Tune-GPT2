import React, { useState } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import './Chatbot.css';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);

  const handleSendMessage = (messageText) => {
    const newMessages = [...messages, { text: messageText, sender: 'user' }];
    setMessages(newMessages);

    // Simulate a bot response after a short delay
    setTimeout(() => {
      setMessages([...newMessages, { text: "I'm a bot, how can I assist?", sender: 'bot' }]);
    }, 1000);
  };

  return (
    <div className="chatbot-container">
      <MessageList messages={messages} />
      <MessageInput onSend={handleSendMessage} />
    </div>
  );
};

export default Chatbot;
