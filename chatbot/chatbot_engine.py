from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

faq_data = [
    {"question": "How can I reset my password?", "answer": "Click 'Forgot password' on the login page."},
    {"question": "What are your working hours?", "answer": "We work 9 AM to 5 PM, Monday to Friday."},
    {"question": "How do I contact support?", "answer": "Email us at support@example.com."},
]

questions = [item["question"] for item in faq_data]
answers = [item["answer"] for item in faq_data]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(questions)

greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
keywords = {
    "password": "You can reset your password by clicking 'Forgot password' on the login page.",
    "support": "You can contact support via email: support@example.com.",
    "hours": "Our working hours are 9 AM to 5 PM, Monday to Friday.",
    "working hours": "We are available from 9 AM to 5 PM, Monday to Friday.",
}

def get_faq_answer(user_input):
    user_input_lower = user_input.lower().strip()

    if any(greet in user_input_lower for greet in greetings):
        return "Hello! How can I assist you today?"


    for keyword, response in keywords.items():
        if keyword in user_input_lower:
            return response

    user_vec = vectorizer.transform([user_input])
    similarities = cosine_similarity(user_vec, X)
    best_match_idx = similarities.argmax()

    if similarities[0][best_match_idx] < 0.3:
        return "Sorry, I didn't understand that. Could you rephrase it?"

    return answers[best_match_idx]
