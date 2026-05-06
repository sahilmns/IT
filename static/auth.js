document.addEventListener("mousemove", (e) => {
    let x = e.clientX / window.innerWidth;
    let y = e.clientY / window.innerHeight;

    document.querySelectorAll(".blob").forEach((blob, index) => {
        let speed = (index + 1) * 20;
        blob.style.transform = `translate(${x * speed}px, ${y * speed}px)`;
    });
});