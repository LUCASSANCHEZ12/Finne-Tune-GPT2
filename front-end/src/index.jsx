import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";

import BotMessage from "./components/BotMessage";
import UserMessage from "./components/UserMessage";
import Messages from "./components/Messages";
import Input from "./components/Input";

import API from "./ChatbotAPI.jsx";

import "./styles.css";
import Header from "./components/Header";

function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [isInputDisabled, setIsInputDisabled] = useState(false);

  useEffect(() => {
    async function loadWelcomeMessage() {
      setMessages([
        <BotMessage
          key="0"
          fetchMessage={async () => await API.GetChatbotResponse("hi")}
        />
      ]);
    }
    loadWelcomeMessage();
  }, []);

  const send = async text => {
    // Deshabilita el input cuando el usuario envía el mensaje
    setIsInputDisabled(true);
  
    // Añade los mensajes del usuario y del bot, pero no hagas la llamada a la API aquí
    const newMessages = messages.concat(
      <UserMessage key={messages.length + 1} text={text} />,
      <BotMessage
        key={messages.length + 2}
        fetchMessage={async () => {
          const response = await API.GetChatbotResponse(text);
          // Aquí puedes procesar la respuesta si es necesario
          // Rehabilita el input una vez que el bot haya respondido
          setIsInputDisabled(false);
          return response;
        }}
      />
    );
  
    // Actualiza los mensajes
    setMessages(newMessages);
  };
  

  return (
    <div className="container">
        <Header />
        <Messages messages={messages} />
        <Input onSend={send} isDisabled={isInputDisabled}/>
    </div>
  );
}

const rootElement = document.getElementById("root");
ReactDOM.render(<Chatbot />, rootElement);
