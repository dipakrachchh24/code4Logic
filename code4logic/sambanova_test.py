from sambanova import SambaNova
import os

client = SambaNova(
    api_key=os.getenv("SAMBANOVA_API_KEY"),
    base_url="https://api.sambanova.ai/v1",
)

response = client.chat.completions.create(
    model="gpt-oss-120b",
    messages=[{"role":"system","content":"You are a helpful assistant"},{"role":"user","content":"Hello!"}],
    temperature=0.1,
    top_p=0.1
)

print(response.choices[0].message.content)