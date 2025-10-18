// Zaman AI Assistant - Frontend Logic

const API_BASE_URL = 'http://localhost:8000/api';
let userId = localStorage.getItem('zaman_user_id') || generateUserId();
let currentMode = 'text';
let mediaRecorder = null;
let audioChunks = [];

// Генерация User ID
function generateUserId() {
    const id = 'user_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('zaman_user_id', id);
    return id;
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadUserProfile();
    loadUserGoals();
    loadUserChallenges();
});

// Event Listeners
function initializeEventListeners() {
    // Mode switching
    document.getElementById('text-mode-btn').addEventListener('click', () => switchMode('text'));
    document.getElementById('voice-mode-btn').addEventListener('click', () => switchMode('voice'));
    
    // Text mode
    document.getElementById('send-btn').addEventListener('click', sendTextMessage);
    document.getElementById('message-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendTextMessage();
    });
    
    // Voice mode
    document.getElementById('record-btn').addEventListener('click', toggleRecording);
}

// Переключение режимов
function switchMode(mode) {
    currentMode = mode;
    
    // Update buttons
    document.getElementById('text-mode-btn').classList.toggle('active', mode === 'text');
    document.getElementById('voice-mode-btn').classList.toggle('active', mode === 'voice');
    
    // Update containers
    document.getElementById('text-input-container').classList.toggle('hidden', mode !== 'text');
    document.getElementById('voice-input-container').classList.toggle('hidden', mode !== 'voice');
}

// Отправка текстового сообщения
async function sendTextMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    input.value = '';
    addMessageToChat('user', message);
    
    // Disable input
    const sendBtn = document.getElementById('send-btn');
    sendBtn.disabled = true;
    sendBtn.textContent = 'Думаю...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                message: message,
                mode: 'text'
            })
        });
        
        const data = await response.json();
        
        // Add assistant response
        addMessageToChat('assistant', data.response, data.suggested_products, data.emotion);
        
        // Update emotion display
        updateEmotionDisplay(data.emotion);
        
    } catch (error) {
        console.error('Error:', error);
        addMessageToChat('assistant', 'Извините, произошла ошибка. Попробуйте ещё раз.');
    } finally {
        sendBtn.disabled = false;
        sendBtn.textContent = 'Отправить';
    }
}

// Запись голоса
async function toggleRecording() {
    const recordBtn = document.getElementById('record-btn');
    const voiceStatus = document.getElementById('voice-status');
    
    if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        // Start recording
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                await sendVoiceMessage(audioBlob);
                
                // Stop stream
                stream.getTracks().forEach(track => track.stop());
            };
            
            mediaRecorder.start();
            recordBtn.classList.add('recording');
            recordBtn.querySelector('.record-text').textContent = 'Нажмите чтобы остановить';
            voiceStatus.textContent = '🔴 Идёт запись...';
            
        } catch (error) {
            console.error('Microphone error:', error);
            voiceStatus.textContent = '❌ Ошибка доступа к микрофону';
        }
    } else {
        // Stop recording
        mediaRecorder.stop();
        recordBtn.classList.remove('recording');
        recordBtn.querySelector('.record-text').textContent = 'Нажмите для записи';
        voiceStatus.textContent = '⏳ Обработка...';
    }
}

// Отправка голосового сообщения
async function sendVoiceMessage(audioBlob) {
    const voiceStatus = document.getElementById('voice-status');
    
    try {
        // Convert to base64
        const reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        
        reader.onloadend = async () => {
            const base64Audio = reader.result.split(',')[1];
            
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    mode: 'voice',
                    audio_data: base64Audio
                })
            });
            
            const data = await response.json();
            
            // Add messages to chat
            addMessageToChat('user', '🎤 Голосовое сообщение');
            addMessageToChat('assistant', data.response, data.suggested_products, data.emotion);
            
            // Update emotion
            updateEmotionDisplay(data.emotion);
            
            // Play audio response if available
            if (data.audio_response) {
                playAudioResponse(data.audio_response);
            }
            
            voiceStatus.textContent = '✓ Готов к записи';
        };
        
    } catch (error) {
        console.error('Error:', error);
        voiceStatus.textContent = '❌ Ошибка отправки';
        addMessageToChat('assistant', 'Извините, произошла ошибка при обработке голоса.');
    }
}

// Воспроизведение аудио ответа
function playAudioResponse(base64Audio) {
    const audio = new Audio('data:audio/mp3;base64,' + base64Audio);
    audio.play().catch(err => console.error('Audio playback error:', err));
}

// Добавление сообщения в чат
function addMessageToChat(role, message, products = [], emotion = null) {
    const chatContainer = document.getElementById('chat-container');
    
    // Remove welcome message if exists
    const welcomeMsg = chatContainer.querySelector('.welcome-message');
    if (welcomeMsg) welcomeMsg.remove();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const now = new Date();
    const time = now.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    
    let productsHtml = '';
    if (products && products.length > 0) {
        productsHtml = `
            <div class="suggested-products">
                <h5>Рекомендуемые продукты:</h5>
                ${products.map(p => `<span class="product-tag">${p}</span>`).join('')}
            </div>
        `;
    }
    
    messageDiv.innerHTML = `
        <div class="message-content">
            ${message}
            ${productsHtml}
            <div class="message-time">${time}</div>
        </div>
    `;
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Обновление отображения эмоций
function updateEmotionDisplay(emotion) {
    if (!emotion) return;
    
    const emotionIcons = {
        'стресс': '😰',
        'тревога': '😟',
        'спокойствие': '😊',
        'радость': '😄',
        'разочарование': '😔'
    };
    
    const icon = emotionIcons[emotion.emotion_type] || '😊';
    document.querySelector('.emotion-type').textContent = `${icon} ${emotion.emotion_type}`;
    document.getElementById('stress-score').textContent = emotion.stress_score.toFixed(1);
    
    // Color code stress level
    const stressScore = document.getElementById('stress-score');
    if (emotion.stress_score >= 7) {
        stressScore.style.color = '#d32f2f';
    } else if (emotion.stress_score >= 5) {
        stressScore.style.color = '#ffa726';
    } else {
        stressScore.style.color = '#66bb6a';
    }
}

// Загрузка профиля пользователя
async function loadUserProfile() {
    try {
        const response = await fetch(`${API_BASE_URL}/profile/${userId}`);
        const data = await response.json();
        
        updateEmotionDisplay({
            emotion_type: data.dominant_emotion,
            stress_score: data.average_stress_score
        });
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

// Загрузка целей
async function loadUserGoals() {
    try {
        const response = await fetch(`${API_BASE_URL}/goals/${userId}`);
        const goals = await response.json();
        
        const goalsContainer = document.getElementById('goals-list');
        
        if (goals.length === 0) {
            goalsContainer.innerHTML = '<p class="empty-state">Цели не установлены</p>';
            return;
        }
        
        goalsContainer.innerHTML = goals.map(goal => `
            <div class="goal-item">
                <h4>${goal.title}</h4>
                <p>${goal.current_amount.toLocaleString()} / ${goal.target_amount.toLocaleString()} ₸</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${goal.progress_percentage}%"></div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading goals:', error);
    }
}

// Загрузка челленджей
async function loadUserChallenges() {
    try {
        const response = await fetch(`${API_BASE_URL}/challenges/${userId}`);
        const challenges = await response.json();
        
        const challengesContainer = document.getElementById('challenges-list');
        
        if (challenges.length === 0) {
            challengesContainer.innerHTML = '<p class="empty-state">Нет активных челленджей</p>';
            return;
        }
        
        challengesContainer.innerHTML = challenges.map(challenge => `
            <div class="challenge-item">
                <h4>${challenge.title}</h4>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${challenge.progress_percentage}%"></div>
                </div>
                <p style="font-size: 0.9rem; margin-top: 5px;">
                    ${challenge.progress_percentage.toFixed(1)}% завершено
                </p>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading challenges:', error);
    }
}

// Check proactive notifications periodically
setInterval(async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/proactive/check/${userId}`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.has_notification) {
            addMessageToChat('assistant', data.message);
        }
    } catch (error) {
        console.error('Error checking proactive notifications:', error);
    }
}, 300000); // Every 5 minutes

