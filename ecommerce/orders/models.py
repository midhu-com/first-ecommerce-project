from django.db import models
from accounts.models import Account
from category.models import Category
from store.models import Product,Variation
from django.core.validators import MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError

class Payment(models.Model):

    COD = 'COD'
    PAYPAL = 'Paypal'
    WALLET = 'Wallet'
    WALLET_AND_PAYPAL= 'WalletandRazorpay'

    PAYMENT_METHOD_CHOICES = [
    (COD, 'COD'),
    (PAYPAL, 'PAYPAL'),
    (WALLET, 'Wallet'),
    (WALLET_AND_PAYPAL, 'Wallet and Paypal'),  # Corrected value
    ]

    # Payment status choices
    PENDING = 'Pending'
    COMPLETED = 'Completed'
    REFUNDED = 'Refunded'

    PAYMENT_STATUS_CHOICES = [
    (PENDING, 'Pending'),
    (REFUNDED, 'Refunded'),
    (COMPLETED, 'Completed'),
    ]

    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    payment_id=models.CharField(max_length=100)
    payment_method=models.CharField(max_length=100,choices=PAYMENT_METHOD_CHOICES, default=COD)
    amount_paid=models.CharField(max_length=100) #total amount
    payment_status=models.CharField(max_length=100,choices=PAYMENT_STATUS_CHOICES, default=PENDING)
    created_at=models.DateTimeField(auto_now_add=True)

    
    

    def __str__(self):
        return self.payment_id
    

class Order(models.Model):
    STATUS=(
        ('Processing','Processing'),
        ('Shipped','Shipped'),
        ('Cancelled','Cancelled'),
        ('Returned','Returned'),
        ('Delivered','Delivered'),

    )
    user=models.ForeignKey(Account,on_delete=models.SET_NULL,null=True)
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL,null=True,blank=True)
    order_number=models.CharField(max_length=20)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    phone=models.CharField(max_length=15)
    email=models.EmailField(max_length=50)
    address_line_1=models.CharField(max_length=20)
    address_line_2=models.CharField(max_length=20,blank=True)
    country=models.CharField(max_length=20)
    state=models.CharField(max_length=20)
    city=models.CharField(max_length=20)
    order_note=models.CharField(max_length=20,blank=True)
    order_total=models.FloatField()
    tax=models.FloatField()
    status=models.CharField(max_length=20,choices=STATUS,default='Processing')
    coupon = models.CharField(max_length=100, blank=True, null=True)  # Example field for coupon
    final_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Example field for final_total
    ip=models.CharField(max_length=20,blank=True)
    is_ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    original_total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discounted_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    coupon_discount  = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # New field for delivery charge


   
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return self.first_name
    
    def cancel_order(self):
        # Method to cancel the order
        if self.status == 'Processing':
            # Restock products
            for item in self.items.all():
                item.quantity += item.quantity
                item.save()

            self.status = 'Canceled'
            self.save()

            if self.status == 'Completed' :
                user_wallet = self.user.wallet
                user_wallet.add_funds(self.discounted_total)
                self.payment_status = 'Refunded'
                self.save()

            return True
        return False


  
    def ship_order(self):
        # Method to cancel the order
        if self.status == 'Processing':
            # Restock products
            
            self.status ='Shipped'
            self.save()
            return True

        return False

  
    def deliver_order(self):
        # Method to cancel the order
        if self.status == 'Shipped':
            self.status = 'Delivered'
            self.save()

            if self.payment_status == 'Pending' :
                self.payment_status = 'Completed'
                self.save()
            return True
        return False


    def return_order(self):
        # Method to return the order
        if self.status == 'Delivered':
            # Restock products
            for item in self.items.all():
                item.size.stock += item.quantity
                item.size.save()

            self.status = 'Refunded'
            self.save()

            if self.status == self.Completed:
                # Refund the payment if it was completed
                user_wallet = self.user.wallet
                user_wallet.add_funds(self.discounted_total)
                self.payment_status = 'Refunded'
                self.save()

            return True
        return False


    def get_order_history(self):
        # Method to get order history for the user
        return Order.objects.filter(user=self.user).order_by('-created_at')

    def get_order_status_display(self):
        # Method to get display text for order status
        return dict(self.STATUS)[self.status]
    
    def total_value(self):
        # Method to calculate the total order value
        total_value = sum(item.total_price() for item in self.items.all())
        self.total_value = total_value
        self.save()
        return total_value



class OrderProduct(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL,null=True,blank=True)
    user=models.ForeignKey(Account,on_delete=models.SET_NULL,null=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variations=models.ManyToManyField(Variation,blank=True)
    quantity=models.IntegerField()
    product_price=models.FloatField()
    ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.product_name
    

class Address(models.Model):
   
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class Coupon(models.Model):
    code = models.CharField(max_length=50,unique=True)
    discount = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    minimum_purchase_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    maximum_discount_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    def is_valid(self): 
        now =  timezone.now()
        return self.valid_from <= now <=self.valid_to
    def clean(self):
        if self.valid_to and self.valid_to < timezone.now():
            raise ValidationError("Valid to date cannot be in the past.")
    
class Wallet(models.Model):
    user = models.OneToOneField(Account,on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10,decimal_places=2,default=0)

    def __str__(self):
        return f"{self.user.username}'s Wallet"
    
class ProductOffers(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='offer')
    name = models.CharField(max_length=100, default="Default Offer Name")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MaxValueValidator(50)])
    start_date = models.DateField()
    end_date = models.DateField()

class CategoryOffers(models.Model):
    category = models.OneToOneField(Category, on_delete=models.CASCADE, related_name='offer')
    name = models.CharField(max_length=100, default="Default Offer Name")  # Provide a default value
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2 ,validators=[MaxValueValidator(50)])
    start_date = models.DateField()
    end_date = models.DateField()
    

        





