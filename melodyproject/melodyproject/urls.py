
from django.contrib import admin
from django.urls import path
from melodyapp import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_view
from melodyapp.forms import LoginForm,MyPasswordResetForm


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index),
    path('about/',views.about,name="about"),
    path('contact/',views.contact,name="contact"),
    path('category/<slug:val>',views.Categoryview.as_view(),name="category"),
    path('category-title/<val>',views.CategoryTitle.as_view(),name="category-title"),
    path('productdetails/<int:pk>',views.Product_details.as_view(),name="product-details"),
    
    path('profile/',views.ProfileView.as_view(),name='profile'),
    path('address/',views.address,name='address'),

    #for login 
    #1st registartion
    path('registration/',views.CustromerRegistrationView.as_view(),name='customerrigestration'),
      #login authentication 
    path('accounts/login/',auth_view.LoginView.as_view(template_name='login.html',authentication_form=LoginForm),name='login'),
     #password reset
    path('password-reset/',auth_view.PasswordResetView.as_view(template_name='password_reset.html',form_class=MyPasswordResetForm),name='password_reset'),

    #logout
    path('logout/',views.ulogout),

    #increment and decrement


    #add to cart
    path('add-to-cart/',views.add_to_cart,name='add-to-cart'), #add product
    path('cart/',views.show_cart,name='showcart'), # dispay cart page
    path('checkout/',views.checkout.as_view(),name='checkout'),
    path('orders/',views.orders,name='orders'),
    #placeoreder
    #payment
    path('paymentdone/',views.payment_done,name='paymentdone'),
    path('search/',views.search,name='search'),
    
    path('updateqty/<x>/<cid>/',views.updateqty),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # path('orders/',views.orders,name='orders'),

]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

admin.site.site_header="Melody Studio"
admin.site.site_title="Melody Stdio"
admin.site.site_index_title="Welcome to Melody Stdio"