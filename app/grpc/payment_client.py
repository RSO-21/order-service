import grpc
from app.grpc.payment_pb2 import CreatePaymentRequest
from app.grpc.payment_pb2_grpc import PaymentServiceStub
import os

host = os.getenv("PAYMENT_GRPC_HOST", "localhost")
port = os.getenv("PAYMENT_GRPC_PORT", "50051")

channel = grpc.insecure_channel(f"{host}:{port}")
stub = PaymentServiceStub(channel)

def create_payment(order_id: int, user_id: int, amount: float):
    return stub.CreatePayment(
        CreatePaymentRequest(
            order_id=order_id,
            user_id=user_id,
            amount=amount,
            currency="EUR",
            payment_method="CARD",
            provider="MOCK"
        )
    )
