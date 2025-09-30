def handle_response(text: str, bot_username: str) -> str:
    processed: str = text.lower()
    if "hello" in processed or "hi" in processed:
        return "Hello there! How can I assist you today? 🌠"
    elif "how are you" in processed:
        return "I'm just a bot, but thanks for asking! How can I help you? 🤖"
    elif "what is your name" in processed:
        return f"My name is Galaxy Trail Bot {bot_username}. I'm here to assist you! 🚀"
    else:
        return "I'm not sure how to respond to that. Can you ask something else? 🌌"


