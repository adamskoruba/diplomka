const data = [];

const listeners = [];

function subscribe(callback) {
    listeners.push(callback);
}

function notify() {
    listeners.forEach(callback => callback(data));
}

function addData(value) {
    data.push(value);

    if (data.length > 10) {
        data.shift();
    }

    notify();
}


subscribe((data) => {
    const logs = document.getElementById('logs');

    logs.innerHTML = '';

    data.slice(-10).reverse().forEach(item => {
        const div = document.createElement('div');
        div.textContent = item;
        logs.appendChild(div);
    });
});


function addClickListener() {
    document.addEventListener('click', (event) => {
        addData(`bolo kliknute isTrusted=${event.isTrusted} element=${event.target.tagName} id=${event.target.id}
        x=${event.clientX} y=${event.clientY} jeStred=${isClickedInCenter(event.target, event.clientX, event.clientY)}`);
        const dot = document.createElement("div");

        dot.style.position = "fixed";
        dot.style.left = `${event.clientX}px`;
        dot.style.top = `${event.clientY}px`;
        dot.style.width = "12px";
        dot.style.height = "12px";
        dot.style.background = "red";
        dot.style.borderRadius = "50%";
        dot.style.transform = "translate(-50%, -50%)";
        dot.style.zIndex = "10";
        dot.style.pointerEvents = "none";

        document.body.appendChild(dot);

        setTimeout(() => {
            dot.remove();
        }, 2000);
    });
}

function isClickedInCenter(target, clickedX, clickedY) {
    const rect = target.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    return Math.abs(clickedX - centerX) < 1 && Math.abs(clickedY - centerY) < 1;
}

addClickListener();