from django.contrib import admin
from .models import User, Category, Product, ProductImage, Address, Order, OrderItem, Cart, CartItem, Review

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Review)