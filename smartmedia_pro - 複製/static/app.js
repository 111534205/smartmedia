function play(url, title, channel) {
    fetch("/click", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, channel, url })
    });
    window.open(url, "_blank");
}

document.querySelectorAll(".nav").forEach(btn => {
    btn.onclick = () => {
        const list = btn.parentElement.querySelector(".list");
        const scrollAmount = 600; // 每次滑動約 2-3 部影片的距離
        if (btn.classList.contains("right")) {
            list.scrollLeft += scrollAmount;
        } else {
            list.scrollLeft -= scrollAmount;
        }
    }
});