import numpy as np
from sklearn.linear_model import LinearRegression
from collections import defaultdict
from base.models import Product, SalesOrder

class ProductSalesPredictor:
    def __init__(self):
        self.models = {}
        self.products = []
        self._load_data_and_train()

    def _load_data_and_train(self):

        product_sales_map = defaultdict(list)

        sales_qs = SalesOrder.objects.order_by('date_ordered').values('product_id', 'quantity')

        for sale in sales_qs:
            product_sales_map[sale['product_id']].append(sale['quantity'])
        self.products = []
        for product_id, sales in product_sales_map.items():
            product = Product.objects.get(id=product_id)
            self.products.append({
                'id': product.id,
                'name': product.name,
                'sales': sales
            })

        self._train_models()

    def _train_models(self):
        self.models = {}
        for product in self.products:
            sales = product.get('sales', [])
            if len(sales) < 2:
                continue

            X = np.arange(len(sales)).reshape(-1, 1)
            y = np.array(sales).reshape(-1, 1)

            model = LinearRegression()
            model.fit(X, y)

            self.models[product['id']] = model

    def predict_top_sellers(self, future_step=1, top_k=3):
        predictions = []
        for product in self.products:
            model = self.models.get(product['id'])
            if model:
                next_time = np.array([[len(product['sales']) + future_step - 1]])
                predicted_sales = model.predict(next_time)[0][0]

                predictions.append({
                    'id': product['id'],
                    'name': product['name'],
                    'predicted_sales': round(predicted_sales, 2)
                })

        predictions.sort(key=lambda x: x['predicted_sales'], reverse=True)
        return predictions[:top_k]
