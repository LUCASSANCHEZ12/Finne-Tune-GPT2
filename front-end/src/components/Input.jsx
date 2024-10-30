import React, { useState } from "react";

export default function Input({ onSend, isDisabled}) {
  const [text, setText] = useState("");

  const handleInputChange = e => {
    setText(e.target.value);
  };

  const sendPromptToModel = e => {
    e.preventDefault();
    onSend(text);
    setText("");
  };

  return (
    <div className="input" id="input">
      <form onSubmit={sendPromptToModel}>
        <input
          type="text"
          onChange={handleInputChange}
          value={text}
          placeholder="Enter your message here"
          disabled={isDisabled}
        />
        <button>
          <svg
            version="1.1"
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 500 500"
          >
            <g>
              <g>
                <polygon points="0,497.25 535.5,267.75 0,38.25 0,216.75 382.5,267.75 0,318.75" />
              </g>
            </g>
          </svg>
        </button>
      </form>
    </div>
  );
}
