from groq import Groq
client = Groq()
completion = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "user",
            "content": "Give me a Python code snippet that prints 'Hello, World!'"
        }
    ]
)
print(completion.choices[0].message.content)