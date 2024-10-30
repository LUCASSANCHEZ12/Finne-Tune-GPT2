const API = {
  GetChatbotResponse: async message => {
    return new Promise(function(resolve, reject) {
      console.log("Sending message to chatbot model: ", message);
      setTimeout(function() {
        if (message === "hi") resolve("Welcome to chatbot!");
        else resolve("echo : " + message);
      }, 2000);
    });
  }
};

export default API;
