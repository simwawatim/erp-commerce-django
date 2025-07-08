from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .main import ProductSalesPredictor

predictor = ProductSalesPredictor()

@method_decorator(csrf_exempt, name='dispatch')
class PredictView(View):
    def get(self, request):
        try:
            future_step = int(request.GET.get('future_step', 1))
            top_k = int(request.GET.get('top_k', 3))
            predictions = predictor.predict_top_sellers(future_step, top_k)
            return JsonResponse({'predictions': predictions})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
