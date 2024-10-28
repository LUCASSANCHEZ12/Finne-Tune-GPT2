const API = {
  GetChatbotResponse: async message => {
    const input = document.querySelector("#input");

    return new Promise(function(resolve, reject) {
      
      input.disabled = true;

      setTimeout(function() {
        if (message === "hi") resolve("Welcome to chatbot!");
        else resolve("echo : " + message);
      }, 2000);

      input.disabled = false;

    });
  }
};

export default API;
