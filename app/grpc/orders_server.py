import grpc
from concurrent import futures
from google.protobuf.timestamp_pb2 import Timestamp

from app.database import get_db_session
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
        with get_db_session(schema='public') as db:
            try:
                orders = db.query(models.OrderLookup).filter(
                    models.OrderLookup.user_id == request.user_id
                ).all()

                pb_orders = []
                for o in orders:
                    # 1. VARNA PRETVORBA DATUMA
                    # Če uporabljaš string v proto:
                    date_str = o.created_at.isoformat() if o.created_at else ""
                    
                    # 2. VARNO USTVARJANJE OBJEKTA
                    # Odstranila sva 'id', zato ga tukaj NE SME BITI.
                    # Uporabi točna imena polj, kot jih imaš v .proto datoteki!
                    summary = orders_pb2.OrderSummary(
                        external_id=str(o.external_id) if o.external_id else "",
                        user_id=str(o.user_id) if o.user_id else "",
                        order_status=str(o.order_status) if o.order_status else "unknown",
                        tenant_id=str(o.tenant_id) if o.tenant_id else "",
                        partner_id=str(o.partner_id) if o.partner_id else "",
                        order_id=int(o.order_id) if o.order_id else 0,
                        total_amount=float(o.total_amount) if o.total_amount else 0.0,
                        created_at=to_timestamp(o.created_at) # ali pb_timestamp, če uporabljaš Timestamp
                    )
                    pb_orders.append(summary)

                return orders_pb2.GetOrdersByUserResponse(orders=pb_orders)

            except Exception as e:
                # Ta print boš videla v logih order-service-1
                print(f"!!! TO JE NAPAKA: {type(e).__name__}: {str(e)}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Lookup error: {str(e)}")
                return orders_pb2.GetOrdersByUserResponse()

    def GetOrderById(self, request, context):
        order_id = request.order_id

        metadata = dict(context.invocation_metadata())
        tenant_id = metadata.get("x-tenant-id", "public")

        with get_db_session(schema=tenant_id) as db:
            try:
                o = db.query(models.Order).filter(models.Order.id == order_id).first()

                if not o:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Order not found")
                    return orders_pb2.GetOrderByIdResponse()

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

                if o.partner_id is not None:
                    pb_order.partner_id = o.partner_id
                if o.payment_id is not None:
                    pb_order.payment_id = o.payment_id

                return orders_pb2.GetOrderByIdResponse(order=pb_order)

            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"DB error: {e}")
                return orders_pb2.GetOrderByIdResponse()


def serve_grpc(host="0.0.0.0", port=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    orders_pb2_grpc.add_OrdersServiceServicer_to_server(OrdersService(), server)
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    return server
