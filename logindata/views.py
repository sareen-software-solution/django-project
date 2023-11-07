from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User, AnonymousUser
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DeleteView, UpdateView, ListView
from logindata.form import RegistrationForm, ProductUpdateForm
from logindata.models import Product, Cart, CartItem, Order, OrderItem


# Create your views here.

class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')


class ProductView(View):
    def get(self, request):
        data = Product.objects.all()
        return render(request, 'products.html', {'data': data})


class ProductSearchView(ListView):
    model = Product
    template_name = 'products-search.html'  # Create this template
    context_object_name = 'search_results'
    paginate_by = 10

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')
        if search_query:
            return Product.objects.filter(name__icontains=search_query)
        else:
            return Product.objects.all()


class ProductAddView(View):
    def get(self, request):
        return render(request, 'add-product.html')

    def post(self, request):
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        Product.objects.create(name=name, description=description, price=price)
        return redirect('products')


class ProductDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'logindata.delete_product'
    model = Product
    template_name = 'delete-product.html'
    success_url = reverse_lazy('products')


class ProductUpdateView(PermissionRequiredMixin,UpdateView):
    permission_required = 'logindata.change_product '
    model = Product
    form_class = ProductUpdateForm
    template_name = 'edit-product.html'
    success_url = reverse_lazy('products')


class CartView(View):
    def get(self, request):
        if request.user and not isinstance(request.user, AnonymousUser):
            user = request.user
        else:
            user, created = User.objects.get_or_create(username='guest')
        cart, created = Cart.objects.get_or_create(user=user)
        total_price = cart.calculate_total_price()
        return render(request, 'cart.html', {'cart': cart, 'total_price': total_price})

    def post(self, request):
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        product = get_object_or_404(Product, pk=product_id)
        if request.user and not isinstance(request.user, AnonymousUser):
            user = request.user
        else:
            user, created = User.objects.get_or_create(username='guest')
        cart, created = Cart.objects.get_or_create(user=user)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()
        else:
            cart_item.quantity = int(quantity)
            cart_item.save()
        return redirect('cart')


@login_required
def payment(request):
    cart = Cart.objects.get(user=request.user)
    for cart_item in cart.cartitem_set.all():
        order = Order(client_name=request.user)
        order.save()
        order_item = OrderItem(order=order, product=cart_item.product, quantity=cart_item.quantity)
        order_item.save()
    cart.cartitem_set.all().delete()
    return redirect('order-create')


def order_create(request):
    orders = Order.objects.filter(client_name=request.user, status='Pending')
    return render(request, 'order-create.html', {'orders': orders})


def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'You have successfully logged in.')
                return redirect('products')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def custom_logout(request):
    logout(request)
    return redirect('login')


def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Error creating your account. Please correct the errors below.')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

