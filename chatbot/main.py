from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .chatbot_engine import get_faq_answer

class FAQChatbotView(APIView):
    def post(self, request):
        message = request.data.get('message')

        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        response = get_faq_answer(message)
        return Response({'response': response})
