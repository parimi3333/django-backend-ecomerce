from django.db import models
from datetime import datetime

# Create your models here.

class Order(models.Model):
    orderid = models.CharField(max_length=100)
    email = models.EmailField()
    prodid = models.CharField(max_length=100)
    order_product = models.CharField(max_length=100)
    order_amount = models.CharField(max_length=25)
    order_payment_id = models.CharField(max_length=100, blank=True)
    isPaid = models.BooleanField(default=False)
    order_date = models.DateTimeField(default=datetime.now(), blank=True)

    def __str__(self):
        return self.order_product
