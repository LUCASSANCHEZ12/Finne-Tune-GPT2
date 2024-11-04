# Finne-Tune-GPT2

## Collaborators
- **Lucas Sanchez**
  - GitHub: [`LUCASSANCHEZ12`](https://github.com/LUCASSANCHEZ12)
- **Gabriel Villarreal**
  - GitHub: [`GabrielVillarrealPonce`](https://github.com/GabrielVillarrealPonce)
- **Nicolas Vargas**
  - GitHub: [`kI0r203`](https://github.com/kI0r203)

## Objective
This project was created as a task for the *"Topicos selectos en Inteligencia Artificial"* course at *Universidad Privada Boliviana* (UPB).

## Project Description
**Finne-Tune-GPT2** is a chatbot specifically designed to answer questions about Bolivian laws. The chatbot is powered by a fine-tuned LLM model named `LLaMa 3.2 3b from META` model, making it capable of understanding and responding to various legal queries accurately.

## Framework and Technologies
- Website Framework: `React`
- AI Model Language: `Python`
- Web service: `Python FastAPI`

## Data Collection for Training Dataset

To gather data, an exhaustive search for documents, reports, and relevant files in the domain of Bolivian legislation was conducted, including laws, decrees, and official codes. Key documents included the Political Constitution of the State, the Bolivian Penal Code, the Child and Adolescent Code, and the Tax Code.

Given the required level of transformation to adapt these documents to a training format, each was meticulously preprocessed. To create the dataset, we utilized prompt engineering, prompting a model to generate specific and inferential questions about each article of each law. The resulting questions and answers were structured in a CSV file following the format:

I, Q, A
1, "", ""
2, "", ""
...

This approach yielded a total of 4,000 questions and answers focused on Bolivian legislation. The variety and precision of the generated questions not only diversified the dataset but also prepared the model for real-world consultation and analysis scenarios in a legal context.

## Website Functionality
The website features a chat between the model and the user. 

## How to Use
The application is a basic Chat between the model and the user.
1. Start the application
2. Submit your own question using the provided input prompt.
3. Wait for the model to answer after thinking about the propvided prompt.

## Installation
To run the project locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone [https://github.com/LUCASSANCHEZ12/Sentiment_Analyzer.git](https://github.com/LUCASSANCHEZ12/Finne-Tune-GPT2.git)
    ```

2. Install all Python dependencies
    ```bash
    cd back-end
    pip install -r requirements.txt
    ```

### Installing React on Linux and Windows

To install React, you first need to set up Node.js and npm (Node Package Manager), which are required to manage the React dependencies. Below are the instructions for both Linux and Windows.

#### Installing React on Linux

1. **Update your package index**
   ```bash
   sudo apt update
   ```

2. **Install Node.js and npm**
   ```bash
   sudo apt install nodejs npm
   ```

3. **Verify the installation**
   - Check Node.js version:
     ```bash
     node -v
     ```
   - Check npm version:
     ```bash
     npm -v
     ```

4. **Install Create React App**
   ```bash
   sudo npm install -g create-react-app
   ```

5. **Create a new React project**
   ```bash
   npx create-react-app my-app
   ```

6. **Run the React app**
   ```bash
   cd my-app
   npm start
   ```

#### Installing React on Windows

1. **Download Node.js and npm**
   - Go to the [Node.js website](https://nodejs.org/) and download the installer for Windows.
   - Follow the installation steps, making sure to include npm.

2. **Verify the installation**
   - Open Command Prompt and check Node.js version:
     ```cmd
     node -v
     ```
   - Check npm version:
     ```cmd
     npm -v
     ```

3. **Install Create React App**
   ```cmd
   npm install -g create-react-app
   ```

4. **Create a new React project**
   ```cmd
   npx create-react-app my-app
   ```

5. **Run the React app**
   ```cmd
   cd my-app
   npm start
   ```

After completing these steps, the React development server will run, and you can view your application in the browser at `http://localhost:3000`.


## Lauch the project

1. Start the python API:
    Inside of `back-end/`
    * For Linux and Windows
    ```bash
      python3 api.py
    ```
    
2. Start the React development server:
    Inside of `front-end/`
    ```bash
    npm install
    npm start
    ```

3. Navigate to `http://localhost:3000/` in your browser.

## Contributing
If you wish to contribute to the project, please fork the repository and submit a pull request.

## Acknowledgements
We would like to thank the Universidad Privada Boliviana (UPB) and our internship manager for the guidance and support throughout this project.

Feel free to contact us for any queries or feedback.

*Cochabamba, Bolivia*
*November, 2024*
