from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_session, verify_token
from sqlalchemy.orm import Session
from schemas import OrderSchema, OrderItemSchema, ResponseOrderSchema
from models import Order, User, OrderItens
from typing import List

order_router = APIRouter(prefix="/orders", tags=["Orders"], dependencies=[Depends(verify_token)])

@order_router.get("/")
async def orders():
    """
    Default route for the order module.

    This endpoint serves as the base route for the order system.
    It confirms that the order service is active and reachable.
    All routes within the `orders` module require authentication
    to ensure secure access.

    Returns:
        dict: A JSON object containing a simple confirmation message.
    """
    return {"response": "You have accessed the order route"}

@order_router.post("/order")
async def order(
    order_schema: OrderSchema,
    user: User = Depends(verify_token), 
    session: Session =  Depends(get_session)
    ):
    """
    Create a new order.

    This endpoint allows an authenticated user to create a new order record.
    Only administrators or users creating an order for themselves are authorized
    to perform this action. Unauthorized attempts result in a 403 Forbidden error.

    The newly created order is stored in the database and returns its ID upon success.

    Args:
        order_schema (OrderSchema): The payload containing order data, including the `user_id`.
        user (User): The authenticated user making the request, obtained from the JWT token.
        session (Session): SQLAlchemy database session dependency.

    Raises:
        HTTPException: If a non-admin user attempts to create an order for another user (status code 403).

    Returns:
        dict: A JSON object containing a success message and the ID of the newly created order.
    """
    if not user.admin and user.id != order_schema.user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to make this request.")
    else:
        new_order = Order(user=order_schema.user_id)
        session.add(new_order)
        session.commit()
        return {"response": f"Order created successfully. Order ID: {new_order.id}"}

    
@order_router.get("/list")
async def list_orders(
    user: User = Depends(verify_token), 
    session: Session =  Depends(get_session)
    ):
    """
    Retrieve the list of all orders.

    This endpoint returns all orders stored in the database.  
    Access is restricted to admin users only — non-admin users
    attempting to access this route will receive a 403 Forbidden error.

    Args:
        user (User): The authenticated user obtained from the JWT token.
        session (Session): SQLAlchemy database session dependency.

    Raises:
        HTTPException: If the user is not an admin (status code 403).

    Returns:
        dict: A JSON object containing:
            - `orders_list` (list): A list of all order records from the database.
    """
    if not user.admin:
        raise HTTPException(status_code=403, detail="You are not authorized to make this request.")
    else:
        orders_list = session.query(Order).all()
        return {
            "orders_list": orders_list
        }

@order_router.get("/list/orders_user/{user_id}", response_model=List[ResponseOrderSchema])
async def list_user_orders(
    user_id: int,
    user: User = Depends(verify_token), 
    session: Session =  Depends(get_session)
    ):
    """
    Retrieve all orders for a specific user.

    This endpoint returns all orders associated with the given `user_id`.  
    Access is restricted to either the user themselves or an admin user.
    Non-admin users attempting to access orders of other users will receive
    a 403 Forbidden error.

    Args:
        user_id (int): The ID of the user whose orders are being requested.
        user (User): The authenticated user obtained from the JWT token.
        session (Session): SQLAlchemy database session dependency.

    Raises:
        HTTPException: If the authenticated user is not an admin and
            attempts to access another user's orders (status code 403).

    Returns:
        List[ResponseOrderSchema]: A list of order records for the specified user,
        serialized according to the `ResponseOrderSchema`.
    """
    if not user.admin and user.id != user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to make this request.")
    else:
        user_orders_list = session.query(Order).filter(Order.user == user_id).all()
        return user_orders_list
        
@order_router.get("/order/{order_id}")
async def get_order(
    order_id: int,
    user: User = Depends(verify_token), 
    session: Session =  Depends(get_session)
    ):
    """
    Retrieve details of a specific order by its ID.

    This endpoint fetches a single order from the database based on the provided `order_id`.
    Access is restricted to the user who owns the order or an admin user.  
    Non-admin users attempting to access another user's order will receive a 403 Forbidden error.
    If the order does not exist, a 400 Bad Request error is returned.

    Args:
        order_id (int): The ID of the order to retrieve.
        user (User): The authenticated user obtained from the JWT token.
        session (Session): SQLAlchemy database session dependency.

    Raises:
        HTTPException: If the order does not exist (status code 400).
        HTTPException: If the authenticated user is not an admin and
            attempts to access another user's order (status code 403).

    Returns:
        dict: A JSON object containing:
            - `qnt_order_itens` (int): The number of items in the order.
            - `order` (Order): The full order object, including all details.
    """
    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Order not found.")
    if not user.admin and user.id != order.user:
        raise HTTPException(status_code=403, detail="You are not authorized to make this request.")
    return {
        "qnt_order_itens": len(order.itens),
        "order": order
    }
        
@order_router.post("/order/add_item/{order_id}")
async def add_iten_order(
    order_id: int,
    order_item_schema: OrderItemSchema,
    user: User = Depends(verify_token), 
    session: Session =  Depends(get_session)
    ):
    """
    Add a new item to an existing order.

    This endpoint allows an authenticated user to add a new item to a specific order.
    Access is restricted to the user who owns the order or an admin user.
    Unauthorized users attempting to modify another user's order will receive a 403 Forbidden error.
    If the order does not exist, a 400 Bad Request error is returned.

    After adding the item, the total price of the order is recalculated and stored.

    Args:
        order_id (int): The ID of the order to which the item will be added.
        order_item_schema (OrderItemSchema): The payload containing item details,
            including quantity, flavor, size, and unit price.
        user (User): The authenticated user obtained from the JWT token.
        session (Session): SQLAlchemy database session dependency.

    Raises:
        HTTPException: If the order does not exist (status code 400).
        HTTPException: If the authenticated user is not an admin and
            attempts to modify another user's order (status code 403).

    Returns:
        dict: A JSON object containing:
            - `response` (str): Confirmation message indicating successful creation.
            - `order_item_id` (int): The ID of the newly created order item.
            - `order_price` (float): The updated total price of the order.
    """
    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Order not found.")
    if not user.admin and user.id != order.user:
        raise HTTPException(status_code=403, detail="You are not authorized to make this request.")
    order_item = OrderItens(
        order_item_schema.quantity,
        order_item_schema.flavor,
        order_item_schema.size,
        order_item_schema.unit_price,
        order_id
        )
    session.add(order_item)
    order.calculate_price()
    session.commit()
    return {
        "response": "Item created successfully",
        "order_item_id": order_item.id,
        "order_price": order.price
    }

@order_router.post("/order/remove_item/{order_item_id}")
async def remove_iten_order(
    order_item_id: int,
    user: User = Depends(verify_token), 
    session: Session =  Depends(get_session)
    ):
    """
    Remove an item from an existing order.

    This endpoint allows an authenticated user to delete a specific item from an order.
    Access is restricted to the user who owns the order or an admin user.  
    Unauthorized attempts to remove items from another user's order result in a 403 Forbidden error.
    If the item does not exist, a 400 Bad Request error is returned.

    After removing the item, the total price of the order is recalculated and stored.

    Args:
        order_item_id (int): The ID of the order item to be removed.
        user (User): The authenticated user obtained from the JWT token.
        session (Session): SQLAlchemy database session dependency.

    Raises:
        HTTPException: If the order item does not exist (status code 400).
        HTTPException: If the authenticated user is not an admin and
            attempts to modify another user's order (status code 403).

    Returns:
        dict: A JSON object containing:
            - `response` (str): Confirmation message indicating successful deletion.
            - `order_itens` (list): The updated list of remaining items in the order.
            - `order` (Order): The updated order object, including recalculated price.
    """
    order_item = session.query(OrderItens).filter(OrderItens.id == order_item_id).first()
    if not order_item:
        raise HTTPException(status_code=400, detail="Item not found.")
    order = session.query(Order).filter(Order.id == order_item.order).first()
    if not user.admin and user.id != order.user:
        raise HTTPException(status_code=403, detail="You are not authorized to make this request.")
    session.delete(order_item)
    order.calculate_price()
    session.commit()
    return {
        "response": "Item deleted successfully",
        "order_itens": order.itens,
        "order": order
    }
    
@order_router.post("order/cancel/{order_id}")
async def cancel_order(
    order_id: int,
    user: User = Depends(verify_token), 
    session: Session =  Depends(get_session)
    ):
    """
    Cancel an existing order.

    This endpoint allows an authenticated user to cancel a specific order.
    Only the user who owns the order or an admin user can perform this action.
    Unauthorized attempts to cancel another user's order result in a 403 Forbidden error.
    If the order does not exist, a 400 Bad Request error is returned.

    The order's status is updated to `"canceled"` in the database.

    Args:
        order_id (int): The ID of the order to cancel.
        user (User): The authenticated user obtained from the JWT token.
        session (Session): SQLAlchemy database session dependency.

    Raises:
        HTTPException: If the order does not exist (status code 400).
        HTTPException: If the authenticated user is not an admin and
            attempts to cancel another user's order (status code 403).

    Returns:
        dict: A JSON object containing:
            - `response` (str): Confirmation message indicating successful cancellation.
            - `order` (Order): The updated order object with the status set to `"canceled"`.
    """
    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Order not found.")
    if not user.admin and user.id != order.user:
        raise HTTPException(status_code=403, detail="You are not authorized to make this request.")
    order.status = "canceled"
    session.commit()
    return {
        "response": f"Order {order.id} canceled successfully.",
        "order": order
    }
    
@order_router.post("order/complete/{order_id}")
async def complete_order(
    order_id: int,
    user: User = Depends(verify_token), 
    session: Session =  Depends(get_session)
    ):
    """
    Mark an existing order as completed.

    This endpoint allows an authenticated user to complete a specific order.
    Only the user who owns the order or an admin user can perform this action.
    Unauthorized attempts to complete another user's order result in a 403 Forbidden error.
    If the order does not exist, a 400 Bad Request error is returned.

    The order's status is updated to `"completed"` in the database.

    Args:
        order_id (int): The ID of the order to mark as completed.
        user (User): The authenticated user obtained from the JWT token.
        session (Session): SQLAlchemy database session dependency.

    Raises:
        HTTPException: If the order does not exist (status code 400).
        HTTPException: If the authenticated user is not an admin and
            attempts to complete another user's order (status code 403).

    Returns:
        dict: A JSON object containing:
            - `response` (str): Confirmation message indicating successful completion.
            - `order` (Order): The updated order object with the status set to `"completed"`.
    """
    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Order not found.")
    if not user.admin and user.id != order.user:
        raise HTTPException(status_code=403, detail="You are not authorized to make this request.")
    order.status = "completed"
    session.commit()
    return {
        "response": f"Order {order.id} completed successfully.",
        "order": order
    }