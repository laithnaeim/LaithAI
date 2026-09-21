import os
from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Roblox Luau AI Studio</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: sans-serif; }
        body { display: flex; height: 100vh; background-color: #1a1a1a; color: #ffffff; }
        .sidebar { width: 250px; background-color: #111111; padding: 20px; border-right: 1px solid #333; }
        .logo { font-size: 20px; font-weight: bold; color: #00a2ff; margin-bottom: 30px; }
        .chat-container { flex: 1; display: flex; flex-direction: column; height: 100%; }
        .chat-header { padding: 20px; background-color: #161616; border-bottom: 1px solid #333; font-weight: bold; }
        .chat-messages { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; }
        .message { max-width: 75%; padding: 12px 16px; border-radius: 8px; line-height: 1.5; }
        .user-message { background-color: #00a2ff; color: white; align-self: flex-end; }
        .ai-message { background-color: #262626; color: #e0e0e0; align-self: flex-start; white-space: pre-wrap; font-family: monospace; }
        .chat-input-area { padding: 20px; background-color: #161616; border-top: 1px solid #333; display: flex; gap: 10px; }
        textarea { flex: 1; background-color: #262626; border: 1px solid #444; border-radius: 6px; padding: 12px; color: white; resize: none; height: 50px; }
        button { background-color: #00a2ff; color: white; border: none; padding: 0 25px; border-radius: 6px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="logo">Laith AI v1</div>
    </div>
    <div class="chat-container">
        <div class="chat-header">Laith Lua Assistant</div>
        <div class="chat-messages" id="chatMessages">
            <div class="message ai-message">Hello! I am your Roblox Luau AI specialist. What kind of script are we building today?</div>
        </div>
        <div class="chat-input-area">
            <textarea id="userInput" placeholder="Ask for a Roblox script..."></textarea>
            <button id="sendBtn" onclick="sendMessage()">Generate</button>
        </div>
    </div>
    <script>
        async function sendMessage() {
            const inputField = document.getElementById('userInput');
            const sendButton = document.getElementById('sendBtn');
            const chatMessages = document.getElementById('chatMessages');
            const prompt = inputField.value.trim();
            if (!prompt) return;

            const userDiv = document.createElement('div');
            userDiv.className = 'message user-message';
            userDiv.textContent = prompt;
            chatMessages.appendChild(userDiv);
            
            inputField.value = '';
            inputField.disabled = true;
            sendButton.disabled = true;

            const aiDiv = document.createElement('div');
            aiDiv.className = 'message ai-message';
            aiDiv.textContent = "Generating Roblox code...";
            chatMessages.appendChild(aiDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt })
                });
                const data = await response.json();
                aiDiv.textContent = data.response;
            } catch (error) {
                aiDiv.textContent = "Error connecting to server.";
            } finally {
                inputField.disabled = false;
                sendButton.disabled = false;
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    user_data = request.json
    user_prompt = user_data.get("prompt", "")
    
    # DYNAMIC ENVIRONMENT FIX: 
    # Use the dashboard Ngrok variable if present (Render). Otherwise, default to local machine loop.
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Strip any potential accidental trailing slashes to keep URL strings pristine
    base_url = base_url.rstrip('/')
    ollama_url = f"{base_url}/api/generate"
    
    payload = {
        "model": "robloxlua-ai",
        "prompt": user_prompt,
        "stream": False
    }
    try:
        # Added a 60-second timeout buffer to protect connections over cloud relays
        response = requests.post(ollama_url, json=payload, timeout=60)
        return jsonify({"response": response.json().get("response", "No response.")})
    except Exception as e:
        return jsonify({"response": f"Backend Error: {str(e)}"}), 500

if __name__ == '__main__':
    # Force the app to scale dynamically with whatever port Render assigns in the cloud
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
