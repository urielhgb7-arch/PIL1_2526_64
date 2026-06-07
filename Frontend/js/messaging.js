function sendMessage() {
    const input = document.getElementById('msgInput');
    const text = input.value.trim();

    if (!text) return;

    const list = document.getElementById('messagesList');

    const row = document.createElement('div');
    row.className = 'msg-row sent';

    row.innerHTML = `
        <div class="msg-bubble">
            ${text}
            <span class="msg-time">${now()}</span>
        </div>
    `;

    list.appendChild(row);

    input.value = '';
    list.scrollTop = list.scrollHeight;
}