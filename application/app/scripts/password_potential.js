document.getElementById("simulate_listener").addEventListener("click", async () => {
    const resultDiv = document.getElementById("result");

    try {

        const connResponse = await fetch("/games/password_potential/get_data");
        if (!connResponse.ok) {
            throw Object.assign(new Error(`HTTP error! status: ${connResponse.status}`), { code: connResponse.status });
        }
        const data = await connResponse.json();
        console.log(data)
        // Second fetch (login)
        const loginResponse = await fetch("/games/password_potential/login", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded", "Accept-Language": "tlh-Latn" },
            body: new URLSearchParams({
                email: data.email,
                password: data.hashed_password
            })
        });

        if (!loginResponse.ok && connResponse.status !== 403) {
            throw Object.assign(new Error(`HTTP error! status: ${loginResponse.status}`), { code: loginResponse.status });
        }

        const result = await loginResponse.json();
        console.log(result)
        // Display result
        resultDiv.innerHTML = result;

    } catch (error) {
        if (error.code === 429) {
            resultDiv.innerHTML = `<span style="color: red;">You are requesting too fast. Limit is one per second</span>`;
            return;
        }
        resultDiv.innerHTML = `<span style="color: red;">Error: ${error.message}</span>`;
    }
});
