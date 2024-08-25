# Chatbot with Guardrails 🛡️

This repository contains a Streamlit-based chatbot application enhanced with guardrails to ensure safer and more controlled responses from large language models (LLMs). The application leverages the Groq API for LLM interactions and uses NeMo Guardrails to enforce rules on both user inputs and bot outputs.

## Features

- **Asynchronous Execution**: The application utilizes asynchronous functions to interact with the LLMs, ensuring efficient and non-blocking operations.
- **Customizable Guardrails**: The app allows you to define specific rules for both user inputs and bot outputs, ensuring adherence to company policies or other guidelines.
- **Conversation History Management**: Conversations are stored in a `.txt` file upon clearing the conversation history, allowing for easy reference and auditing.
- **Modern UI**: The app features a simple, yet modern UI with custom styling and intuitive interaction patterns.

## Installation

### Prerequisites

- Python 3.7 or higher

### Dependencies

Install the required packages using `pip`:

```bash
pip install -r requirements.txt
```

The `requirements.txt` includes the following dependencies:

- `langchain_groq==0.1.9`
- `nemoguardrails==0.9.1.1`
- `nest_asyncio==1.6.0`
- `streamlit==1.36.0`

### Setting Up

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app**:

   ```bash
   streamlit run automate.py
   ```

## Usage

1. **Start the Chatbot**: After running the Streamlit app, you'll be greeted with a chat interface.
2. **Define Guardrails**: Customize input and output guardrails according to your needs.
3. **Interact**: Ask questions or provide prompts, and observe the responses with and without the guardrails.
4. **Save Conversations**: Conversations are automatically saved when the 'Clear Conversation History' button is clicked, preserving the chat for future reference.

## Project Structure

- **`automate.py`**: The main Streamlit app script that configures the UI and handles the interaction logic.
- **`contents.py`**: Contains the core logic for interacting with the LLMs, generating YAML configurations for guardrails, and managing asynchronous tasks.
- **`requirements.txt`**: Lists the dependencies required for running the application.

## Customization

### Changing Models

You can easily switch between different LLMs by modifying the model selection in `contents.py`.

### Guardrails Configuration

The application allows for extensive customization of guardrails through YAML configurations. Modify the `apply_guardrails` function in `contents.py` to tailor the rules according to your project requirements.

## Contribution

Contributions are welcome! Please feel free to submit a pull request or open an issue to improve the project.

