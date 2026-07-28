import os
import json
import http.client

def analyze_airdrop(protocol):
    api_key = os.environ.get("GROQ_API_KEY")

    prompt = (
        "Protocol: " + protocol["name"] + "\n"
        "Category: " + protocol["category"] + "\n"
        "Chain: " + protocol["chain"] + "\n"
        "TVL: $" + str(round(protocol["tvl"] / 1_000_000, 1)) + "M\n\n"
        "This protocol has no token yet and may do an airdrop.\n"
        "Write maximum 5 steps in Turkish for users to qualify.\n"
        "Only write the steps, nothing else."
    )

    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.3
    }).encode("utf-8")

    try:
        conn = http.client.HTTPSConnection("api.groq.com")
        conn.request(
            "POST",
            "/openai/v1/chat/completions",
            body=payload,
            headers={
                "Authorization": "Bearer " + api_key,
                "Content-Type": "application/json",
            }
        )
        res = conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("Groq hatasi: " + str(e))
        return "Adimlar alinamadi."

if __name__ == "__main__":
    test = {
        "name": "Symbiotic",
        "category": "Restaking",
        "chain": "Ethereum",
        "tvl": 341_000_000
    }
    print(analyze_airdrop(test))