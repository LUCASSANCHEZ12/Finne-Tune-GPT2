const API = {
  GetChatbotResponse: async message => {
    return new Promise(function(resolve, reject) {
      console.log("Sending message to chatbot model: ", message);
      const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ "prompt": message })
    };
    fetch('http://localhost:800/prompt', requestOptions)
        .then(response => response.json())
        .then(data => this.setState({ postId: data.id }));
      setTimeout(function() {
        if (message === "hi") resolve("Welcome to chatbot!");
        else resolve("echo : " + message);
      }, 2000);
    });
  }
};

export default API;
