import grpc
from concurrent import futures
from google.protobuf.timestamp_pb2 import Timestamp

from app.database import get_db
from app import models
from app.grpc import orders_pb2, orders_pb2_grpc


def to_timestamp(dt):
    ts = Timestamp()
    if dt is None:
        return ts
    # dt may be timezone-aware; Timestamp supports it
    ts.FromDatetime(dt)
    return ts


class OrdersService(orders_pb2_grpc.OrdersServiceServicer):
    def GetOrdersByUser(self, request, context):
        user_id = request.user_id

        db_gen = get_db()
        db = next(db_gen)
        try:
            orders = db.query(models.Order).filter(models.Order.user_id == user_id).all()

            pb_orders = []
            for o in orders:
                pb_items = [
                    orders_pb2.OrderItem(
                        id=it.id,
                        order_id=it.order_id,
                        offer_id=it.offer_id,
                        quantity=it.quantity,
                    )
                    for it in (o.items or [])
                ]

                pb_order = orders_pb2.Order(
                    id=o.id,
                    user_id=o.user_id,
                    order_status=o.order_status,
                    payment_status=o.payment_status,
                    created_at=to_timestamp(o.created_at),
                    updated_at=to_timestamp(o.updated_at),
                    items=pb_items,
                )

                # handle nullable fields (proto3 optional)
                if o.partner_id is not None:
                    pb_order.partner_id = o.partner_id
                if o.payment_id is not None:
                    pb_order.payment_id = o.payment_id

                pb_orders.append(pb_order)

            return orders_pb2.GetOrdersByUserResponse(orders=pb_orders)

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"DB error: {e}")
            return orders_pb2.GetOrdersByUserResponse()

        finally:
            try:
                db.close()
            except Exception:
                pass


def serve_grpc(host="0.0.0.0", port=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    orders_pb2_grpc.add_OrdersServiceServicer_to_server(OrdersService(), server)
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    return server
