// โครงหน้ากากเว็บ - HTML/CSS/JS
export class UiTemplate {
  static getHtml(): string {
    return `
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MotorBoy AI Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(to right, #4facfe, #00f2fe);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 1.1rem;
        }
        
        .chat-container {
            padding: 30px;
            height: 500px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .msg {
            max-width: 80%;
            padding: 12px 18px;
            border-radius: 18px;
            word-wrap: break-word;
            line-height: 1.5;
            margin-bottom: 10px;
        }
        
        .user {
            background: linear-gradient(to right, #4facfe, #00f2fe);
            color: white;
            margin-left: auto;
        }
        
        .ai {
            background: #f8f9fa;
            color: #333;
            border: 1px solid #e9ecef;
        }
        
        .chat-img {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            margin: 10px 0;
        }
        
        .input-container {
            display: flex;
            padding: 20px;
            border-top: 1px solid #eee;
            gap: 10px;
        }
        
        #user-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            font-size: 1rem;
            outline: none;
            transition: all 0.3s ease;
        }
        
        #user-input:focus {
            border-color: #4facfe;
            box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.25);
        }
        
        #send-btn {
            background: linear-gradient(to right, #4facfe, #00f2fe);
            color: white;
            border: none;
            padding: 0 30px;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        #send-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
        }
        
        #send-btn:active {
            transform: translateY(0);
        }
        
        #loading-rider {
            display: none;
            flex-direction: column;
            align-items: center;
            padding: 20px;
            gap: 10px;
        }
        
        #loading-rider .spinner {
            width: 30px;
            height: 30px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #4facfe;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        #loading-rider p {
            color: #666;
            font-style: italic;
        }
        
        .timestamp {
            font-size: 0.75rem;
            opacity: 0.7;
            margin-top: 5px;
            display: block;
        }
        
        .preview-box {
            display: none;
            margin: 15px 0;
            padding: 15px;
            border: 1px dashed #ddd;
            border-radius: 10px;
            text-align: center;
        }
        
        #image-preview {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
        }
        
        #image-input {
            display: none;
        }
        
        .image-btn {
            background: #e9ecef;
            border: none;
            padding: 10px 15px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
        }
        
        .image-btn:hover {
            background: #dee2e6;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .chat-container {
                height: 400px;
            }
            
            .input-container {
                padding: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>MotorBoy AI Assistant</h1>
            <p>ผู้ช่วยอัจฉริยะสำหรับนักบิด</p>
        </div>
        
        <div class="chat-container" id="chat-container">
            <div class="msg ai">
                สวัสดีครับ! ผมคือ MotorBoy AI Assistant ยินดีให้บริการครับ
                <span class="timestamp">เวลาใหม่ล่าสุด</span>
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="user-input" placeholder="พิมพ์ข้อความของคุณที่นี่..." />
            <button id="send-btn">ส่ง</button>
            <button type="button" class="image-btn" onclick="document.getElementById('image-input').click()">
                📷 รูปภาพ
            </button>
            <input type="file" id="image-input" accept="image/*" onchange="previewImage(this)">
        </div>
        
        <div class="preview-box" id="preview-box">
            <img id="image-preview" src="" alt="ภาพตัวอย่าง" />
        </div>
        
        <div id="loading-rider">
            <div class="spinner"></div>
            <p>ช่างซิ่งกำลังคิดคำตอบ...</p>
        </div>
    </div>

    <script>
        let currentImageBase64 = null;

        document.addEventListener('DOMContentLoaded', () => {
            const input = document.getElementById('user-input');
            const btn = document.getElementById('send-btn');
            const container = document.getElementById('chat-container');

            function addMessage(content, isUser = false) {
                const messageDiv = document.createElement('div');
                messageDiv.className = isUser ? 'msg user' : 'msg ai';
                messageDiv.innerHTML = content + \`<span class="timestamp">\${new Date().toLocaleTimeString('th-TH')}</span>\`;
                container.appendChild(messageDiv);
                scrollToBottom();
            }

            function setLoading(isLoading) {
                btn.disabled = isLoading;
                input.disabled = isLoading;
                document.getElementById('loading-rider').style.display = isLoading ? 'flex' : 'none';
                if (isLoading) {
                    btn.innerHTML = 'กำลังประมวลผล...';
                    input.placeholder = 'กำลังคิดคำตอบ...';
                } else {
                    btn.innerHTML = 'ส่ง';
                    input.placeholder = 'พิมพ์ข้อความของคุณที่นี่...';
                }
            }

            async function sendMessage() {
                const input = document.getElementById('user-input');
                const btn = document.getElementById('send-btn');
                let text = input.value.trim();
                if (!text && !currentImageBase64) return;

                input.value = ''; input.disabled = true; btn.disabled = true;
                const container = document.getElementById('chat-container');
                
                let html = \`<div class="msg user">\`;
                if (currentImageBase64) html += \`<img src="\${currentImageBase64}" class="chat-img"><br>\`;
                html += \${text || "📻 ส่งข้อความเสียงด่วนจากหน้างาน"}</div>\`;
                container.innerHTML += html;
                scrollToBottom();

                let activeImg = currentImageBase64;
                currentImageBase64 = null;
                document.getElementById('preview-box').style.display = 'none';

                // 🚨 [ฟีเจอร์อัตโนมัติ]: ระบบแอบเช็คเพื่อสลับข้อความทักทายสั้นๆ ช่วยเซฟ Token
                if (text.length < 4 && (text.includes("ดี") || text.includes("หวัด") || text.includes("hi"))) {
                    text = text + " (ระบบอัตโนมัติ: ตอบทักทายสไตล์ช่างซิ่งแบบสั้นๆ กระชับที่สุด)";
                }

                document.getElementById('loading-rider').style.display = 'flex';
                const aiDiv = document.createElement('div');
                aiDiv.className = 'msg ai'; aiDiv.innerText = '⚡...';
                container.appendChild(aiDiv);
                scrollToBottom();

                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: text, image: activeImg })
                    });
                    document.getElementById('loading-rider').style.display = 'none';
                    if (!response.ok) throw new Error('กล่องไฟชาร์จไม่เข้า');

                    const reader = response.body.getReader();
                    const decoder = new TextDecoder('utf-8');
                    aiDiv.innerText = '';

                    while (true) {
                        const { value, done } = await reader.read();
                        if (done) break;
                        aiDiv.innerText += decoder.decode(value, { stream: true });
                        container.scrollTop = container.scrollHeight;
                    }
                } catch (error) {
                    document.getElementById('loading-rider').style.display = 'none';
                    aiDiv.innerText = '❌ เกิดข้อผิดพลาดระบบไฟ: ' + error.message;
                } finally {
                    input.disabled = false; btn.disabled = false;
                }
            }

            function scrollToBottom() {
                const container = document.getElementById('chat-container');
                container.scrollTop = container.scrollHeight;
            }

            // 🚨 [ฟีเจอร์อัตโนมัติ]: แอบย่อขนาดและบีบอัดรูปภาพทันทีก่อนส่ง เพื่อประหยัด Token ฝั่ง Vision
            function previewImage(input) {
                if (input.files && input.files[0]) {
                    const file = input.files[0];
                    const reader = new FileReader();
                    
                    reader.onload = function(e) {
                        const img = new Image();
                        img.src = e.target.result;
                        img.onload = function() {
                            // สร้าง Canvas ลับเพื่อแอบย่อขนาดภาพอัตโนมัติเหลือความกว้างสูงสุด 700px
                            const canvas = document.createElement('canvas');
                            const MAX_WIDTH = 700;
                            let width = img.width;
                            let height = img.height;

                            if (width > MAX_WIDTH) {
                                height *= MAX_WIDTH / width;
                                width = MAX_WIDTH;
                            }
                            canvas.width = width;
                            canvas.height = height;
                            
                            const ctx = canvas.getContext('2d');
                            ctx.drawImage(img, 0, 0, width, height);
                            
                            // แปลงภาพเป็น JPEG คุณภาพ 70% (ไฟล์จะเล็กลงมาก แต่ AI อ่านรู้เรื่องชัดเจน)
                            currentImageBase64 = canvas.toDataURL('image/jpeg', 0.7);
                            
                            document.getElementById('image-preview').src = currentImageBase64;
                            document.getElementById('preview-box').style.display = 'block';
                        };
                    };
                    reader.readAsDataURL(file);
                }
            }

            // เหตุการณ์คลิกปุ่มส่ง
            btn.addEventListener('click', sendMessage);

            // เหตุการณ์กด Enter ในช่องป้อนข้อความ
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });

            // โฟกัสที่ช่องป้อนข้อความเมื่อโหลดหน้า
            input.focus();
        });
    </script>
</body>
</html>
    `;
  }
  
  static getHTMLContent(): string {
    return this.getHtml();
  }
}