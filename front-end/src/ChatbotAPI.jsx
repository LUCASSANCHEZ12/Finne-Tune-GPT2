const API = {
  GetChatbotResponse: async message => {
    try {
      if (message === "hi"){
        return "Bienvenido. ¿En que puedo ayudarte?"
      }
      const response = await fetch("http://localhost:8000/prompt", {
        method: "POST",
        body: JSON.stringify({
          prompt: message
        }),
        headers: {
          "Content-Type": "application/json; charset=UTF-8"
        }
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const body_response = await response.json();

      if(body_response.response !== ""){
        return body_response.response
      }else{
        return body_response.error
      }

    } catch (error) {
      console.error("Error fetching chatbot response:", error);
      throw error; // opcional, si quieres manejar el error donde se llame a la función
    }
  }
};

export default API;
