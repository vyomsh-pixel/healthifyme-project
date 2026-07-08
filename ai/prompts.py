def build_health_prompt(user_message, profile, history):

    recent_history = history[-3:]

    prompt = f"""
    You are an AI Health Assistant.

    User Profile:
    Name: {profile.get('name')}
    Age: {profile.get('age')}
    Gender: {profile.get('gender')}
    Goal: {profile.get('goal')}
    Activity Level: {profile.get('activity_level')}

    Recent User Health Activity:
    {recent_history}

    User Question:
    {user_message}

    Give:
    - personalized advice
    - concise answers
    - practical suggestions
    - beginner-friendly explanations
    = in less words and bullets when possible

    Keep responses clean and readable.
    """

    return prompt