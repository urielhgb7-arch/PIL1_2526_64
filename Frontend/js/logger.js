const Logger = {
    _toastTimer: null,

    info(msg) {
        console.log(`[INFO] ${msg}`);
    },

    warn(msg, err) {
        console.warn(`[WARN] ${msg}`, err || "");
    },

    error(msg, err) {
        console.error(`[ERROR] ${msg}`, err || "");
        this._showToast(msg, "error");
    },

    success(msg) {
        this._showToast(msg, "success");
    },

    _showToast(msg, type) {
        const el = document.getElementById("toast");
        if (!el) return;
        el.textContent = msg;
        const bg = type === "success"
            ? "bg-success/20 text-success border border-success/30"
            : "bg-destructive/20 text-destructive border border-destructive/30";
        el.className = `fixed top-6 right-6 z-50 px-5 py-3 rounded-xl shadow-2xl text-sm font-medium transition-all ${bg}`;
        el.classList.remove("hidden");
        clearTimeout(this._toastTimer);
        this._toastTimer = setTimeout(() => el.classList.add("hidden"), 3500);
    },
};
