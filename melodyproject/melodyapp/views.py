from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
import razorpay
from .models import OrderPlaced, Payment, Product,Customer ,Cart
from django.db.models import Count
from .forms import CustromerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q

# Create your views here.


def index(request):
    totalitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request,'home.html',locals())

def about(request):
    totalitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request,'about.html',locals())

def contact(request):
    return render(request,'contact.html')

class Categoryview(View):
    def get(self,request,val):
        totalitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
        product=Product.objects.filter(category=val)
        title=Product.objects.filter(category=val).values('title')
        return render(request,'category.html',locals())
    
class CategoryTitle(View):
    def get(self,request,val):
        product=Product.objects.filter(title=val)
        title=Product.objects.filter(category=product[0].category).values('title')
        totalitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
        return render(request,'category.html',locals())

class Product_details(View):
    def get(self,request,pk):
       totalitem=0
       if request.user.is_authenticated:
           totalitem=len(Cart.objects.filter(user=request.user))
       product=Product.objects.get(pk=pk)
       return render(request,'product_details.html',locals())
    
class CustromerRegistrationView(View):
    def get(self,request):
        form=CustromerRegistrationForm()
        totalitem=0
        if request.user.is_authenticated:
           totalitem=len(Cart.objects.filter(user=request.user))
        return render(request,'CustromerRegistration.html',locals())
    
    def post(self,request):
        form=CustromerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Congratulations! User Register Create Successfully")
        else:
             messages.warning(request,"Invalid Input Data")
        return render(request,'CustromerRegistration.html',locals())
    
class ProfileView(View):
    def get(self,request):
        form=CustomerProfileForm()
        totalitem=0
        if request.user.is_authenticated:
           totalitem=len(Cart.objects.filter(user=request.user))
        return render(request,'profile.html',locals())
    def post(self,request):
         form=CustomerProfileForm(request.POST)
         if form.is_valid():
             user=request.user
             name=form.cleaned_data['name']
             locality=form.cleaned_data['locality']
             city=form.cleaned_data['city']
             mobile=form.cleaned_data['mobile']
             pincode=form.cleaned_data['pincode']
             
             reg=Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,pincode=pincode)
             reg.save()
             messages.success(request,"Congratulation Profile Save Successfully")
         else:
            messages.warning(request,"Invalid Input Data")
         return render(request,'profile.html',locals())

def address(request):
    add= Customer.objects.filter(user=request.user)
    totalitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request,'address.html',locals())

def ulogout(request):
    logout(request)
    return redirect("/")
@login_required
def add_to_cart(request):
    user=request.user
    product_id=request.GET.get('prod_id')
    product=Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect("/cart")
@login_required
def show_cart(request):
    user=request.user
    cart=Cart.objects.filter(user=user)
    amount=0
    for p in cart:
        value=p.quantity * p.product.discounted_price
        amount=amount+value
    totalamount=amount+40
    totalitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request,'addtocart.html',locals())

class checkout(View):
    def get(self,request):
        totalitem=0
        if request.user.is_authenticated:
           totalitem=len(Cart.objects.filter(user=request.user))
        user=request.user
        add=Customer.objects.filter(user=user)
        cart_items=Cart.objects.filter(user=user)
        famount=0
        for p in cart_items:
            value=p.quantity * p.product.discounted_price
            famount=famount+value
        totalamount=famount+40
        razoramount=int(totalamount*100)
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))
        data={ "amount": razoramount, "currency": "INR", "receipt": "order_rcptid_12" }
        payment_response = client.order.create(data=data)
        print(payment_response)
        order_id = payment_response['id']
        order_status = payment_response['status']
        if order_status == 'created':
             payment = Payment(
             user=user,
             amount=totalamount,
             razorpay_order_id=order_id,
             razorpay_payment_status=order_status
        )
        payment.save()
        return render(request,'checkout.html',locals())
    
@login_required
def payment_done(request):
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    cust_id = request.GET.get('cust_id')
    
    user = request.user
    
    customer = Customer.objects.get(id=cust_id)
    
    payment = Payment.objects.get(razorpay_order_id=order_id)
    payment.paid = True
    payment.razorpay_payment_id = payment_id
    payment.save()
    
    cart = Cart.objects.filter(user=request.user)
    for c in cart:
        OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity, payment=payment).save()
        c.delete()
    return redirect("orders")

def orders(request):
    order_placed=OrderPlaced.objects.filter(user=request.user)
    return render(request,'orders.html',locals())


@login_required   
# def search(request):
#     query = request.GET.get('search', '')
#     totalitem = 0
#     if request.user.is_authenticated:
#         totalitem = len(Cart.objects.filter(user=request.user))
#     products = Product.objects.filter(Q(title__icontains=query))
#     return render(request, 'search.html', {'products': products, 'query': query})
def search(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    
    query = request.GET.get('search', '')
    if query:
        product = Product.objects.filter(Q(title__icontains=query))
    else:
        product = Product.objects.none()  # Return an empty QuerySet if no query

    context = {
        'totalitem': totalitem,
        'product': product,
        'query': query,
    }
    return render(request, 'search.html', context)

def updateqty(request,x,cid):
    c=Cart.objects.filter(id=cid)
    q=c[0].quantity
    print(c)
    if x=='1':
        q=q+1
    elif q>1:
        q=q-1
    c.update(quantity=q)
    return redirect('/cart')


def remove_from_cart(request, product_id):
    cart_item = Cart.objects.filter(user=request.user, product__id=product_id).first()
    if cart_item:
        cart_item.delete()
        messages.success(request, "Item removed from cart.")
    else:
        messages.error(request, "Cart item not found.")
    return redirect('/cart')
