from django.urls import path
from django.views.generic import TemplateView
from . import views
app_name = 'kaan'
urlpatterns = [
    path('',views.viewAnalysis,name='Analysis'),
    path('predict/',views.predict,name='Predict'),
    path('about/',views.AboutView,name='About'),
    path('update/',views.update,name='Update'),
    path('login/',views.login,name='Login'),
    path('register/',views.register,name='Register'),
    path('analysis/product/',views.product,name='Product'),
]