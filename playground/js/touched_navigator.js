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

            // spoof webdriver
            if (key === "webdriver") {
                return false;
            }

            const value = target[key];
            return typeof value === "function"
                ? value.bind(target)
                : value;
        },

        has(target, key) {
            if (key === "webdriver") return false;
            return key in target;
        }
    })
});