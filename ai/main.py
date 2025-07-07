import numpy as np
import json
from sklearn.linear_model import LinearRegression

class ProductSalesPredictor:
    def __init__(self, json_path="products_data.json"):
        self.products = []
        self.models = {}
        self.json_path = json_path

    def feed_data(self, products):
        self.products = products
        self.models = {}

        # Save to JSON file
        self._save_to_json(products)

        for product in products:
            sales = product.get("sales", [])
            if len(sales) < 2:
                continue

            X = np.arange(len(sales)).reshape(-1, 1)
            y = np.array(sales).reshape(-1, 1)

            model = LinearRegression()
            model.fit(X, y)
            self.models[product["id"]] = model

    def _save_to_json(self, data):
        try:
            with open(self.json_path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving to JSON: {e}")

    def predict_top_sellers(self, future_step=1, top_k=3):
        predictions = []
        for product in self.products:
            model = self.models.get(product["id"])
            if model:
                next_time = np.array([[len(product["sales"]) + future_step - 1]])
                predicted_sales = model.predict(next_time)[0][0]
                predictions.append({
                    "id": product["id"],
                    "name": product["name"],
                    "predicted_sales": round(predicted_sales, 2)
                })

        predictions.sort(key=lambda x: x["predicted_sales"], reverse=True)
        return predictions[:top_k]
