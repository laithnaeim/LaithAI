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
        :root {
            --bg-deep: #1A1A1E;
            --bg-panel: #202024;
            --bg-slate: #2E2E35;
            --bg-slate-light: #383840;
            --border-subtle: #3A3A42;
            --neon-blue: #00A2FF;
            --neon-blue-dim: rgba(0, 162, 255, 0.15);
            --text-primary: #F2F2F5;
            --text-secondary: #9A9AA5;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', -apple-system, sans-serif; }

        body {
            display: flex;
            height: 100vh;
            background-color: var(--bg-deep);
            color: var(--text-primary);
        }

        /* ---------- Sidebar ---------- */
        .sidebar {
            width: 280px;
            background-color: var(--bg-panel);
            border-right: 1px solid var(--border-subtle);
            display: flex;
            flex-direction: column;
            padding: 20px;
            gap: 24px;
        }

        .logo {
            font-size: 19px;
            font-weight: 700;
            color: var(--neon-blue);
            display: flex;
            align-items: center;
            gap: 8px;
            letter-spacing: 0.3px;
        }

        .logo::before {
            content: "";
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--neon-blue);
            box-shadow: 0 0 8px 2px var(--neon-blue);
            display: inline-block;
        }

        .new-chat-btn {
            background-color: var(--bg-slate);
            border: 1px solid var(--border-subtle);
            color: var(--text-primary);
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .new-chat-btn:hover { background-color: var(--bg-slate-light); border-color: var(--neon-blue); }

        .section-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-secondary);
            margin-bottom: 10px;
        }

        .session-list {
            display: flex;
            flex-direction: column;
            gap: 4px;
            overflow-y: auto;
        }

        .session-item {
            padding: 10px 12px;
            border-radius: 7px;
            font-size: 13px;
            color: var(--text-secondary);
            cursor: pointer;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            border: 1px solid transparent;
            transition: all 0.15s ease;
        }
        .session-item:hover { background-color: var(--bg-slate); color: var(--text-primary); }
        .session-item.active {
            background-color: var(--neon-blue-dim);
            color: var(--neon-blue);
            border-color: rgba(0, 162, 255, 0.35);
            font-weight: 600;
        }

        /* ---------- Parameter Panel ---------- */
        .param-panel {
            border-top: 1px solid var(--border-subtle);
            padding-top: 18px;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }

        .param-row { display: flex; flex-direction: column; gap: 8px; }

        .param-header {
            display: flex;
            justify-content: space-between;
            font-size: 12.5px;
            color: var(--text-secondary);
        }

        .param-value {
            color: var(--neon-blue);
            font-weight: 700;
            font-family: 'Consolas', monospace;
        }

        input[type="range"] {
            -webkit-appearance: none;
            width: 100%;
            height: 4px;
            border-radius: 2px;
            background: var(--bg-slate-light);
            outline: none;
        }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 15px;
            height: 15px;
            border-radius: 50%;
            background: var(--neon-blue);
            box-shadow: 0 0 6px 1px rgba(0, 162, 255, 0.6);
            cursor: pointer;
            border: 2px solid #0d0d0f;
        }
        input[type="range"]::-moz-range-thumb {
            width: 15px;
            height: 15px;
            border-radius: 50%;
            background: var(--neon-blue);
            box-shadow: 0 0 6px 1px rgba(0, 162, 255, 0.6);
            cursor: pointer;
            border: 2px solid #0d0d0f;
        }

        .param-hint { font-size: 11px; color: var(--text-secondary); opacity: 0.75; }

        /* ---------- Chat area ---------- */
        .chat-container { flex: 1; display: flex; flex-direction: column; height: 100%; min-width: 0; }

        .chat-header {
            padding: 18px 24px;
            background-color: var(--bg-panel);
            border-bottom: 1px solid var(--border-subtle);
            font-weight: 700;
            font-size: 14.5px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .chat-header .status-dot {
            width: 8px; height: 8px; border-radius: 50%;
            background: #37d67a;
            box-shadow: 0 0 6px 1px rgba(55, 214, 122, 0.7);
        }

        .chat-messages {
            flex: 1;
            padding: 24px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .message {
            max-width: 78%;
            padding: 13px 17px;
            border-radius: 12px;
            line-height: 1.55;
            font-size: 14px;
        }

        .user-message {
            background-color: var(--neon-blue);
            color: #0a0a0c;
            font-weight: 500;
            align-self: flex-end;
            border-bottom-right-radius: 3px;
        }

        .ai-message {
            background-color: var(--bg-panel);
            border: 1px solid var(--border-subtle);
            color: #e0e0e5;
            align-self: flex-start;
            border-bottom-left-radius: 3px;
        }

        .ai-message p { white-space: pre-wrap; margin: 0 0 8px 0; }
        .ai-message p:last-child { margin-bottom: 0; }

        /* Code block with copy button */
        .code-block-wrapper {
            position: relative;
            margin: 10px 0;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border-subtle);
            background-color: #0f0f12;
        }

        .code-block-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 7px 12px;
            background-color: #161619;
            border-bottom: 1px solid var(--border-subtle);
        }

        .code-lang-tag {
            font-size: 11px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-family: 'Consolas', monospace;
        }

        .copy-btn {
            background-color: var(--bg-slate);
            border: 1px solid var(--border-subtle);
            color: var(--text-primary);
            font-size: 11.5px;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: all 0.15s ease;
        }
        .copy-btn:hover { background-color: var(--bg-slate-light); border-color: var(--neon-blue); color: var(--neon-blue); }
        .copy-btn.copied { color: #37d67a; border-color: #37d67a; }

        .code-block-wrapper pre {
            margin: 0;
            padding: 14px;
            overflow-x: auto;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.5;
            color: #d6e2ff;
        }

        /* Loading dots */
        .loading-dots { display: inline-flex; gap: 4px; align-items: center; padding: 4px 0; }
        .loading-dots span {
            width: 7px; height: 7px; border-radius: 50%;
            background-color: var(--neon-blue);
            animation: bounce 1.2s infinite ease-in-out both;
        }
        .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
        .loading-dots span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0.4); opacity: 0.5; }
            40% { transform: scale(1); opacity: 1; }
        }

        /* Input area */
        .chat-input-area {
            padding: 18px 24px;
            background-color: var(--bg-panel);
            border-top: 1px solid var(--border-subtle);
            display: flex;
            gap: 12px;
        }

        textarea {
            flex: 1;
            background-color: var(--bg-slate);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            padding: 13px;
            color: var(--text-primary);
            resize: none;
            height: 52px;
            font-size: 14px;
            transition: border-color 0.15s ease;
        }
        textarea:focus { outline: none; border-color: var(--neon-blue); }

        button#sendBtn {
            background-color: var(--neon-blue);
            color: #0a0a0c;
            border: none;
            padding: 0 26px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 14px;
            cursor: pointer;
            transition: filter 0.15s ease;
        }
        button#sendBtn:hover { filter: brightness(1.1); }
        button#sendBtn:disabled { opacity: 0.5; cursor: not-allowed; }

        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--bg-slate-light); border-radius: 4px; }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="logo">Laith AI v1</div>
        <button class="new-chat-btn" onclick="newSession()">+ New Session</button>

        <div>
            <div class="section-label">Recent Sessions</div>
            <div class="session-list" id="sessionList"></div>
        </div>

        <div class="param-panel">
            <div class="section-label">System Parameters</div>
            <div class="param-row">
                <div class="param-header">
                    <span>Temperature</span>
                    <span class="param-value" id="tempValue">0.70</span>
                </div>
                <input type="range" id="tempSlider" min="0" max="1" step="0.05" value="0.7"
                       oninput="document.getElementById('tempValue').textContent = parseFloat(this.value).toFixed(2)">
                <div class="param-hint">Lower = precise &amp; deterministic scripts. Higher = more creative variation.</div>
            </div>
        </div>
    </div>

    <div class="chat-container">
        <div class="chat-header"><span class="status-dot"></span> Laith Lua Assistant</div>
        <div class="chat-messages" id="chatMessages">
            <div class="message ai-message"><p>Hello! I am your Roblox Luau AI specialist. What kind of script are we building today?</p></div>
        </div>
        <div class="chat-input-area">
            <textarea id="userInput" placeholder="Ask for a Roblox script..." onkeydown="if(event.key==='Enter' && !event.shiftKey){event.preventDefault(); sendMessage();}"></textarea>
            <button id="sendBtn" onclick="sendMessage()">Generate</button>
        </div>
    </div>

    <script>
        // ---------- Mock session sidebar ----------
        const mockSessions = [
            "Leaderboard DataStore Fix",
            "Humanoid Walkspeed Sprint",
            "Kill Brick Script",
            "Simple Shop GUI",
            "Round-based Game Loop"
        ];
        let activeSession = 0;

        function renderSessions() {
            const list = document.getElementById('sessionList');
            list.innerHTML = '';
            mockSessions.forEach((name, i) => {
                const el = document.createElement('div');
                el.className = 'session-item' + (i === activeSession ? ' active' : '');
                el.textContent = name;
                el.onclick = () => { activeSession = i; renderSessions(); };
                list.appendChild(el);
            });
        }
        function newSession() {
            mockSessions.unshift('New Session');
            activeSession = 0;
            renderSessions();
        }
        renderSessions();

        // ---------- Code block detection + copy button ----------
        // Detects fenced code blocks like ```lua ... ``` and renders them
        // with a syntax tag and a "Copy Script" clipboard button.
        function renderAIContent(container, rawText) {
            container.innerHTML = '';
            const fenceRegex = /```([a-zA-Z0-9_+-]*)\\n?([\\s\\S]*?)```/g;
            let lastIndex = 0;
            let match;
            let foundBlock = false;

            const appendParagraph = (text) => {
                if (!text.trim()) return;
                const p = document.createElement('p');
                p.textContent = text;
                container.appendChild(p);
            };

            while ((match = fenceRegex.exec(rawText)) !== null) {
                foundBlock = true;
                appendParagraph(rawText.slice(lastIndex, match.index));

                const lang = (match[1] || 'lua').trim() || 'lua';
                const code = match[2].replace(/\\n$/, '');

                const wrapper = document.createElement('div');
                wrapper.className = 'code-block-wrapper';

                const header = document.createElement('div');
                header.className = 'code-block-header';

                const tag = document.createElement('span');
                tag.className = 'code-lang-tag';
                tag.textContent = lang;

                const copyBtn = document.createElement('button');
                copyBtn.className = 'copy-btn';
                copyBtn.innerHTML = '📋 Copy Script';
                copyBtn.onclick = () => {
                    navigator.clipboard.writeText(code).then(() => {
                        copyBtn.innerHTML = '✅ Copied';
                        copyBtn.classList.add('copied');
                        setTimeout(() => {
                            copyBtn.innerHTML = '📋 Copy Script';
                            copyBtn.classList.remove('copied');
                        }, 1800);
                    });
                };

                header.appendChild(tag);
                header.appendChild(copyBtn);

                const pre = document.createElement('pre');
                const codeEl = document.createElement('code');
                codeEl.textContent = code;
                pre.appendChild(codeEl);

                wrapper.appendChild(header);
                wrapper.appendChild(pre);
                container.appendChild(wrapper);

                lastIndex = fenceRegex.lastIndex;
            }

            appendParagraph(rawText.slice(lastIndex));

            if (!foundBlock) {
                container.innerHTML = '';
                appendParagraph(rawText);
            }
        }

        async function sendMessage() {
            const inputField = document.getElementById('userInput');
            const sendButton = document.getElementById('sendBtn');
            const chatMessages = document.getElementById('chatMessages');
            const temperature = parseFloat(document.getElementById('tempSlider').value);
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
            aiDiv.innerHTML = '<div class="loading-dots"><span></span><span></span><span></span></div>';
            chatMessages.appendChild(aiDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt, temperature: temperature })
                });
                const data = await response.json();
                renderAIContent(aiDiv, data.response || '');
            } catch (error) {
                aiDiv.innerHTML = '';
                const p = document.createElement('p');
                p.textContent = 'Error connecting to server.';
                aiDiv.appendChild(p);
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
    # Optional creativity control from the new Temperature slider (defaults to 0.7)
    try:
        temperature = float(user_data.get("temperature", 0.7))
    except (TypeError, ValueError):
        temperature = 0.7

    # DYNAMIC ENVIRONMENT FIX: 
    # Use the dashboard Ngrok variable if present (Render). Otherwise, default to local machine loop.
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Strip any potential accidental trailing slashes to keep URL strings pristine
    base_url = base_url.rstrip('/')
    ollama_url = f"{base_url}/api/generate"
    
    payload = {
        "model": "qwen2.5:7b",
        "prompt": user_prompt,
        "stream": False,
        "options": {
            "temperature": temperature
        }
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