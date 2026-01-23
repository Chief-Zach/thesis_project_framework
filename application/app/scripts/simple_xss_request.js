async function hashPassword(password) {
    const enc = new TextEncoder();
    const buf = await crypto.subtle.digest("SHA-256", enc.encode(password));
    return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, "0")).join("");
}

function getCookie(name) {
    const cookies = document.cookie.split("; ");
    console.log(cookies)
    for (let cookie of cookies) {
        const [key, value] = cookie.split("=");
        if (key === name) return decodeURIComponent(value);
    }
    return null;
}


function getFlag() {
    (async () =>
    {
        const url = await hashPassword(getCookie("user"))
        const response = await fetch(`${window.location.origin + window.location.pathname}/${url}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                poinplkjnsdgf: await hashPassword(url + "qweuyitifbuwef")
            })
        });

        if (response.status === 200) {
            document.getElementById("result").innerText = await response.text()
        }
    })()
}