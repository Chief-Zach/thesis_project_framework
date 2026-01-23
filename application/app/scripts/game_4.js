document.getElementById("post_listener").addEventListener("click", () => {

    const resultDiv = document.getElementById("result");

    fetch("/games/more_random_text/get_authenticated_user")
        .then(response => {
            if (response.status === 429) {
                const error = new Error(`HTTP error! status: ${response.status}`);
                error.code = response.status;
                throw error;
            }
            return response.json()
        })
        .then(data => {

            return fetch("/games/more_random_text/super_secure_request", {
                method: 'POST',
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data.payload)
            });
        })
        .then(response => response.json())
        .then(result => {

            resultDiv.innerHTML = result;
        })
        .catch(error => {
            if(error.code === 429) {
                resultDiv.innerHTML = `<span style="color: red;">You are requesting hints too fast. Limit is one per second</span>`;
                return
            }

            resultDiv.innerHTML = `<span style="color: red;">Error: ${error.message}</span>`;
        });
});
