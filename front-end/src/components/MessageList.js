import React from 'react';
import './MessageList.css';

const MessageList = ({ messages }) => {
  return (
    <div className="message-list">
      {messages.map((message, index) => (
        <div 
          key={index} 
          className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}
        >
          {message.text}
        </div>
      ))}
    </div>
  );
};

export default MessageList;
