from django.db import models
from store.models import Product,Variation
from accounts.models import Account
from django.urls import reverse

# Create your models here.
class Cart(models.Model):

    cart_id=models.CharField(max_length=250,blank=True)
    date_added=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
    
class Cartitem(models.Model):
    user=models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variations=models.ManyToManyField(Variation,blank=True)
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,null=True,related_name='items')
    quantity=models.IntegerField(default=1)
    is_active=models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name} - {', '.join([str(variation) for variation in self.variations.all()])}"

    def __unicode__(self):
        return self.product
    
    @property
    def stock_info(self):
        stock_info = {}
        for variation in self.variations.all():
            stock_info[variation.variation_category] = variation.stock
        return stock_info

class wishlist(models.Model):
    user=models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    date_added=models.DateTimeField(auto_now_add=True)

    def get_url(self):
        return reverse('product_detaill', args=[self.product.slug])
    
    def __str__(self):
        return f'{self.user.username} - {self.product.product_name}'
   
