from django.db import models
from category.models import Category
from django.urls import reverse
from accounts.models import Account
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date
from django.db.models import Avg,Count
from django.utils.text import slugify

# Create your models here.
class Product(models.Model):
    product_name=models.CharField(max_length=100,unique=True)
    slug=models.SlugField(max_length=100,unique=True)
    description=models.TextField(max_length=100,blank=True)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    images=models.ImageField(upload_to='photos/products')
    stock=models.IntegerField()
    is_available=models.BooleanField(default=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    created_date=models.DateTimeField(auto_now_add=True)
    modified_date=models.DateTimeField(auto_now=True)
    discprice = models.DecimalField(max_digits=15, decimal_places=2,default=10)
    discount = models.IntegerField(verbose_name="Discount Percentage",default=0,validators=[MinValueValidator(0), MaxValueValidator(100)])
    validators=[MinValueValidator(0), MaxValueValidator(100)]



    def get_url(self):
        return reverse('product_detail',args=[self.category.slug,self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.product_name)
        super().save(*args, **kwargs)
    
    def averagereview(self):
        reviews = ReviewRating.objects.filter(product=self,status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    
    def countreview(self):
        reviews = ReviewRating.objects.filter(product=self,status=True).aggregate(count=Count('id'))
        count =  0   
        if reviews['count'] is not None:
            count = float(reviews['count'])
        return count

    def __str__(self):
        return self.product_name
    

    def price_after_discount(self):
        today = date.today()
        discount = 0
        
        # Check for product-specific offer
        if hasattr(self, 'offer') and self.offer.start_date <= today <= self.offer.end_date:
            discount = max(discount, self.offer.discount_percentage)
        
        # Check for category-specific offer
        if hasattr(self.category, 'offer') and self.category.offer.start_date <= today <= self.category.offer.end_date:
            discount = max(discount, self.category.offer.discount_percentage)
        
        if discount > 0:
            return round(self.price * (1 - discount / 100), 2)
        return round(self.price, 2)
    
    def discount_percentage(self):
        today = date.today()
        discount = 0

        # Check for product-specific offer
        if hasattr(self, 'offer') and self.offer.start_date <= today <= self.offer.end_date:
            discount = max(discount, self.offer.discount_percentage)

        # Check for category-specific offer
        if hasattr(self.category, 'offer') and self.category.offer.start_date <= today <= self.category.offer.end_date:
            discount = max(discount, self.category.offer.discount_percentage)

        return discount
        
class Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='product_images/')


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category='color',is_active=True)
    
    def sizes(self):
        return super(VariationManager,self).filter(variation_category='size',is_active=True)

variation_category_choice=(
    ('color', 'color'),
    ('size', 'size'),
)
class Variation(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category=models.CharField(max_length=200,choices=variation_category_choice)
    variation_value=models.CharField(max_length=100)
    is_active=models.BooleanField(default=True)
    created_date=models.DateTimeField(auto_now=True)

    objects=VariationManager()

    def __str__(self):
        return self.variation_value
    
class ReviewRating(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    subject=models.CharField(max_length=100,blank=True)
    review=models.TextField(max_length=500,blank=True)
    rating=models.FloatField()
    ip=models.CharField(max_length=220,blank=True)
    status=models.BooleanField(default= True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.subject
