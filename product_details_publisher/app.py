from fastapi import FastAPI, HTTPException
from dapr.clients import DaprClient
import json
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.post("/publish-orders")
async def publish_orders(product_details: dict):
    try:
        orderId = product_details["orderId"]
        productName = product_details["productName"]
        quantity = product_details["quantity"]
        price = product_details["price"]

        with DaprClient() as client:
            order = {
                'orderId': orderId,
                'productName': productName,
                'quantity': quantity,
                'price': price
            }

            # Publish an event/message using Dapr PubSub
            result = client.publish_event(
                pubsub_name='orderpubsub',
                topic_name='orders',
                data=json.dumps(order),
                data_content_type='application/json',
            )
            logging.info('Published data: ' + json.dumps(order))
            return {"message": f"Order with orderId {orderId} and product {productName} published successfully"}
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"{e} is required in the JSON payload")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
