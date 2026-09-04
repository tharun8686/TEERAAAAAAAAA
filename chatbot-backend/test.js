require('dotenv').config({ path: '../.env' });
async function test() {
    const res = await fetch("https://integrate.api.nvidia.com/v1/chat/completions", {
        method: "POST",
        headers: { 
            "Authorization": `Bearer ${process.env.NV_API_KEY}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            model: "meta/llama2-70b",
            messages: [{role: "user", content: "hello"}]
        })
    });
    console.log(res.status, res.statusText);
    const text = await res.text();
    console.log("Body:", text);
}
test();
