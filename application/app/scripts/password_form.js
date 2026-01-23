document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("loginForm");
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const resultDiv = document.getElementById("result");

        const formData = new FormData(form);

        await fetch(form.action, {
            method: form.method,
            body: formData,
            credentials: 'same-origin'
        })
            .then(response => {
                if (response.status === 429) {
                    const error = new Error(`HTTP error! status: ${response.status}`);
                    error.code = response.status;
                    throw error;
                }
                return response.json()
            })
            .then(result => {
                    resultDiv.innerHTML = result;
                }
            )
            .catch(error => {
            if(error.code === 429) {
                resultDiv.innerHTML = `<span style="color: red;">You are requesting too fast. Limit is one per second</span>`;
                return
            }

            resultDiv.innerHTML = `<span style="color: red;">Error: ${error.message}</span>`;
        });
    })
});
