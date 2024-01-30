from django.shortcuts import redirect
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from datetime import datetime
import traceback
from .models import Order
from users.models import MyUser
from django.db.models import Q
from .serializers import OrderSerializer
from rest_framework.exceptions import NotFound
import numpy as np
import requests

appId=""
secretKey=""

client = MongoClient(settings.URI, server_api=ServerApi('1'))
db = client['products']

def base36encode(collectionname=''):
    counters = decode_result(db['counters'].find({},{"_id":0}))
    newid = np.base_repr(counters[0][collectionname], 36)
    counters[0][collectionname] += 1
    deleting = db['counters'].drop()
    dummy = db['counters'].insert_many(counters)
    return  newid

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, datetime):
            return o.strftime("%d-%m-%Y, %H:%M:%S")
        return super().default(o)

def decode_result(cursor):
    return json.loads(JSONEncoder().encode(list(cursor)))

@api_view(['GET','POST'])
def products(request):
    if request.method == "GET":
        try:
            itemid = request.query_params.get("itemid")
            filters = {}
            if itemid:
                filters["prodid"] = int(itemid)
            specific_feilds = {"_id":0}
            output_list = decode_result(db['items'].find(filters, specific_feilds))
            return Response(output_list,status=status.HTTP_200_OK)
        except:
            return Response(traceback.format_exc(),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def wishlist(request):
    if request.method == "GET":
        try:
            wishid = request.query_params.get("wishid")
            filters = {"email":request.user.email}
            specific_feilds = {}
            if wishid:
                filters['wishid'] = wishid
            output_list = decode_result(db['wishlist'].find(filters, specific_feilds))
            return Response(output_list, status=status.HTTP_200_OK)
        except:
            return Response(traceback.format_exc(),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        try:
            wishid = request.query_params.get("wishid")
            data = request.data
            filters = {}
            specific_feilds = {}
            if wishid:
                output = db['wishlist'].update_one(filters,{"$set":data})
            else:
                data['wishid'] =  base36encode('wishlist')
                data['email'] = request.user.email
                output = db['wishlist'].insert_one(data)
            return Response({"status": "data submitted"}, status=status.HTTP_200_OK)
        except:
            return Response(traceback.format_exc(),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cart(request):
    if request.method == "GET":
        try:
            cartid = request.query_params.get("cartid")
            filters = {"email":request.user.email}
            specific_feilds = {}
            if cartid:
                filters['cartid'] = cartid
            output_list = decode_result(db['cart'].find(filters, specific_feilds))
            return Response(output_list, status=status.HTTP_200_OK)
        except:
            return Response(traceback.format_exc(),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        try:
            cartid = request.query_params.get("cartid")
            data = request.data
            filters = {}
            specific_feilds = {}
            if cartid:
                output = db['cart'].update_one(filters,{"$set":data})
            else:
                data['cartid'] =  base36encode('cart')
                output = db['cart'].insert_one(data)
            return Response({"status": "data submitted"}, status=status.HTTP_200_OK)
        except:
            return Response(traceback.format_exc(),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def ordersapi(request):
    if request.method == "GET":
        try:
            output_list = []
            filters = {"email": request.user.email}
            products = decode_result(db['items'].find({},{"_id":0}))
            if orderid:
                try:
                    orderdata = Order.objects.get(orderid=orderid, **filters)
                    serializer = OrderSerializer(orderdata)
                except Order.DoesNotExist:
                    raise NotFound("Order not found")
            else:
                orderdata = Order.objects.filter(**filters)
                serializer = OrderSerializer(orderdata, many=True)
            serialized_data = serializer.data
            if isinstance(serialized_data, list):
                for item in serialized_data:
                    filtered_data = next((data for data in products if data["prodid"]==item["prodid"]),None)
                    filtered_data['orderid'] = item['orderid']
                    output_list.append(filtered_data)
            else:
                filtered_data = next((data for data in products if data["prodid"]==serialized_data["prodid"]),None)
                filtered_data['orderid'] = item['orderid']
                output_list.append(filtered_data)

            return Response(output_list, status=status.HTTP_200_OK)
        except:
            return Response(traceback.format_exc(),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        try:
            orderid = request.query_params.get("orderid")
            data = request.data
            filters = {"email": request.user.email}
            specific_feilds = {}
            data = request.data
            if orderid:
                orderdata = Order.objects.get(orderid=orderid, **filters)
                serializer = OrderSerializer(orderdata,data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
            else:
                orderdata = {
                            'orderid': base36encode('orders'), 
                            'prodid': str(data.get('prodid')), 
                            'order_product': str(data.get('title')),
                            'order_amount': str(data.get('price')), 
                            'email': request.user.email,  
                            'order_payment_id': "", 
                        }
                print(orderdata)
                serializer = OrderSerializer(data=orderdata)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
            return Response({"status": "data submitted"}, status=status.HTTP_200_OK)
        except:
            return Response(traceback.format_exc(),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def payment(request):
    if request.method == "POST":
        data = request.data
        output_dict = {}
        userdetails = MyUser.objects.get(email=request.user.email)
        url = "https://sandbox.cashfree.com/pg/orders"

        payload = {
            "customer_details": {
                "customer_id": data['orderid'],
                "customer_email": userdetails['email'],
                "customer_phone": userdetails['phone'][3:],
                "customer_name": userdetails['name']
            },
            "order_meta": {
                "return_url": "https://example.com/return?order_id={order_id}",
                "notify_url": "https://example.com/cf_notify",
                "payment_methods": "cc,nb,dc"
            },
            "order_id": data['orderid'],
            "order_amount": data['price'],
            "order_currency": "INR"
        }
        headers = {
            "accept": "application/json",
            "x-api-version": "2022-09-01",
            "content-type": "application/json",
            "x-client-id": appId,
            "x-client-secret": secretKey
        }

        response = requests.post(url, json=payload, headers=headers)

        payment_data = json.loads(response.text)
        orderdata = Order.objects.get(orderid= data["orderid"])
        serializer = OrderSerializer(orderdata,data={"order_payment_id":payment_data["payment_session_id"]},partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        output_dict["payment_session_id"] = payment_data["payment_session_id"]
        return output_dict

@api_view(["POST"])
def cfresponse(request):
    if request.method == "POST":
        try:
            ResponseData = request.data
            if ResponseData['data']['payment']['payment_status'] == "SUCCESS":
                orderdata = Order.objects.get(orderid= ResponseData['order']['order_id'])
                serializer = OrderSerializer(orderdata,data={"isPaid":True},partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
            return Response({"status": "updated"},status=status.HTTP_200_OK)
        except:
            return Response(traceback.format_exc(),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def returnurl(request):
    if request.method == "GET":
        orderid = request.query_params.get("order_id")
        params = ""

        url = f"https://sandbox.cashfree.com/pg/orders/{orderid}" # for prod "https://api.cashfree.com/pg/orders/{orderid}

        headers = {
            "accept": "application/json",
            "x-api-version": "2022-09-01",
            "x-client-id": appId,
            "x-client-secret": secretKey
        }
        response = requests.get(url, headers=headers)
        payment_data = json.loads(response.text)
        params = 'orderid=' + orderid + '&txn-status=' + payment_data["order_status"]
        if payment_data["order_status"] == "PAID":
            params += '&payment=success'
        else:
            params += '&payment=pending'
        return redirect("http://localhost:3000//payment_status/pgcf?" + params) 