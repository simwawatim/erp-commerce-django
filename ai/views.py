from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from .main import ProductSalesPredictor

predictor = ProductSalesPredictor()

@method_decorator(csrf_exempt, name='dispatch')
class FeedView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            products = data.get("products", [])
            if not products:
                return JsonResponse({"error": "No products provided"}, status=400)
            predictor.feed_data(products)
            return JsonResponse({"message": "Product data fed successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class PredictView(View):
    def get(self, request):
        try:
            future_step = int(request.GET.get("future_step", 1))
            top_k = int(request.GET.get("top_k", 3))
            predictions = predictor.predict_top_sellers(future_step, top_k)
            return JsonResponse({"predictions": predictions})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
