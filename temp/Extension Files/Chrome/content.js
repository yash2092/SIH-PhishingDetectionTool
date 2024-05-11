var url = location.href;

let url_parsed = url.split('/');
let full_domain = url_parsed[2];

if(!url.includes("http://127.0.0.1:3000"))
{
fetch("http://127.0.0.1:5000/Predict", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
    },
    body: JSON.stringify({ url: url }),
})
    .then((res) => {
        if (res.ok) {
            return res.json();
        } else {
            throw new Error("Failed to fetch data");
        }
    })
    .then((record) => {
        console.log(record)
        const detectionResult = record.detectionResult; // Assuming 1 indicates Phishing and 0 indicates Safe

        // Display the result on the page

        if (detectionResult == 1) {
            if (confirm("SecurePhish Chrome Extension: We have found a phishing website! Do you want to continue?")) {
                // location.href = 'https://secure-phish.vercel.app/home?url=' + url;

            }
            else {
                location.href = 'http://127.0.0.1:3000/features';
            }
        } else {
            alert("Website is ok!");
        }
    })
    .catch((error) => {
        alert("SecurePhish Chrome Extension: Oops! Looks like we have an error! " + error)
    });
}
console.log(full_domain)