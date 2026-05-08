const originalNavigator = window.navigator;

Object.defineProperty(window, "__navLog", {
    value: [],
    writable: true
});

window.__navLog.push("nav logger initialized");

Object.defineProperty(window, "navigator", {
    value: new Proxy(originalNavigator, {
        get(target, key) {
            const prop = String(key);

            const msg = `navigator.${prop} accessed`;
            console.log(msg);
            window.__navLog.push(msg);

            const value = target[key];

            return typeof value === "function"
                ? value.bind(target)
                : value;
        }
    }),
    writable: false,
    configurable: false
});