import pytest
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import Client
from django.urls import reverse

from logindata.form import RegistrationForm
from logindata.models import Product, CartItem, Cart, Order, OrderItem


# Create your tests here.
@pytest.mark.django_db
def test_index_view():
    client = Client()
    url = reverse('index')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_product_view():
    client = Client()
    url = reverse('products')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_product_view_render():
    client = Client()
    product1 = Product.objects.create(name='shirt', price=10.0)
    product2 = Product.objects.create(name='jeans', price=15.0)
    response = client.get(reverse('products'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_product_search_view():
    client = Client()
    product1 = Product.objects.create(name='Apple', price=1.0)
    product2 = Product.objects.create(name='Banana', price=2.0)
    product3 = Product.objects.create(name='Cherry', price=3.0)
    response = client.get(reverse('search_products'))
    assert response.status_code == 200
    response = client.get(
        reverse('search_products') + '?search=Banana')
    assert response.status_code == 200


@pytest.mark.django_db
def test_product_search_view():
    client = Client()

    product1 = Product.objects.create(name='jacket', price=170.0)
    product2 = Product.objects.create(name='jeans', price=150.0)
    search_term = 'jacket'
    response = client.get(reverse('search_products') + f'?search={search_term}')
    assert response.status_code == 200

    assert 'search_results' in response.context

    search_results = response.context['search_results']
    assert product1 in search_results
    assert product2 not in search_results

    search_term = 'Non-Existent Product'
    response = client.get(reverse('search_products') + f'?search={search_term}')
    assert response.status_code == 200

    assert 'search_results' in response.context

    search_results = response.context['search_results']
    assert not search_results


@pytest.mark.django_db
def test_product_add_view():
    client = Client()
    url = reverse('add_products')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_product_add_view_post():
    client = Client()
    url = reverse('add_products')
    data = {
        'name': 'coca-cola',
        'description': 'very tasty cold drink',
        'price': int('19'),
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('products')
    assert Product.objects.filter(name='coca-cola', description='very tasty cold drink', price=19.99).exists()


@pytest.mark.django_db
def test_product_delete_view():
    client = Client()
    product = Product.objects.create(name='Product to Delete', description='Description', price=10.0)
    url = reverse('delete_product', args=[product.pk])
    response = client.post(url, follow=True)
    assert response.status_code == 200
    products = Product.objects.filter(pk=product.pk)
    assert not products.exists()


@pytest.mark.django_db
def test_product_delete_view_post():
    client = Client()
    product = Product.objects.create(name='Test Product', price=10.0)
    response = client.post(reverse('delete_product', args=[product.id]), follow=True)
    assert response.status_code == 200
    assert not Product.objects.filter(id=product.id).exists()
    assert response.redirect_chain[-1] == (reverse('products'), 302)


@pytest.mark.django_db
def test_product_update_view():
    client = Client()
    product = Product.objects.create(name='Original Product', description='Description', price=10.0)
    url = reverse('update_product', args=[product.pk])
    response = client.get(url)
    assert response.status_code == 200
    updated_data = {
        'name': 'Updated Product',
        'description': 'Updated Description',
        'price': 15.0,
    }
    response = client.post(url, updated_data)
    assert response.status_code == 302
    assert response.url == reverse('products')
    updated_product = Product.objects.get(pk=product.pk)
    assert updated_product.name == 'Updated Product'
    assert updated_product.description == 'Updated Description'
    assert (updated_product.price == 15.0)


@pytest.mark.django_db
def test_product_update_view():
    client = Client()
    product = Product.objects.create(name='Fridge', description=' GOOD NEW FRIDGE', price=200.0)
    url = reverse('update_product', args=[product.pk])
    response = client.get(url)
    assert response.status_code == 200
    updated_data = {
        'name': 'television',
        'description': 'a good new tv',
        'price': 150.0,
    }
    response = client.post(url, updated_data)
    assert response.status_code == 302
    assert response.url == reverse('products')
    updated_product = Product.objects.get(pk=product.pk)
    assert updated_product.name == 'television'
    assert updated_product.description == 'a good new tv'
    assert updated_product.price == 150.0


@pytest.mark.django_db
def test_cart_view_post_and_delete_cart_item():
    client = Client()
    user = User.objects.create_user(username='pushkar', password='coderslab')
    product = Product.objects.create(name='Test Product', price=10.0)
    cart = Cart.objects.create(user=user)
    data = {
        'product_id': product.id,
        'quantity': 3,
    }
    client.force_login(user)
    response = client.post(reverse('cart'), data)
    assert response.status_code == 302
    cart_item = CartItem.objects.get(cart=cart, product=product)
    assert cart_item.quantity == 3
    response = client.post(reverse('cart'), data={'product_id': product.id, 'quantity': 0})  # Assuming '0' means delete
    assert response.status_code == 302
    cart_item_exists = CartItem.objects.filter(pk=cart_item.pk).exists()
    assert cart_item_exists


@pytest.mark.django_db
def test_payment_view():
    client = Client()
    user = User.objects.create_user(username='pushkar', password='coderslab')
    client.force_login(user)
    cart = Cart.objects.create(user=user)
    product = Product.objects.create(name='Test Product', price=10.0)
    cart_item = CartItem.objects.create(cart=cart, product=product, quantity=3)

    response = client.post(reverse('payment'))

    assert response.status_code == 302
    assert response.url == reverse('order-create')

    cart_items = CartItem.objects.filter(cart=cart)
    assert not cart_items.exists()

    orders = Order.objects.filter(client_name=user)
    assert orders.exists()
    order = orders.first()
    assert OrderItem.objects.filter(order=order, product=product, quantity=3).exists()


@pytest.mark.django_db
def test_order_create_view():
    client = Client()
    user = User.objects.create_user(username='pushkar', password='coderslab')
    client.force_login(user)
    order = Order.objects.create(client_name=user, status='Pending')
    response = client.get(reverse('order-create'))

    assert response.status_code == 200
    orders = response.context['orders']
    assert order in orders
    content = str(response.content)
    assert str(order.client_name) in content
    assert str(order.status) in content


@pytest.mark.django_db
def test_custom_login_valid_credentials():
    client = Client()
    user = User.objects.create_user(username='pushkar', password='coderslab')
    data = {
        'username': 'pushkar',
        'password': 'coderslab',
    }
    response = client.post(reverse('login'), data)
    assert response.status_code == 302
    assert response.url == reverse('products')


@pytest.mark.django_db
def test_custom_login_invalid_credentials():
    client = Client()
    user = User.objects.create_user(username='pushkar', password='coderslab')
    data = {
        'username': 'pushkar',
        'password': 'coderslab2023',
    }
    response = client.post(reverse('login'), data)
    assert response.status_code == 200
    assert b'Invalid username or password.' in response.content


@pytest.mark.django_db
def test_custom_logout():
    client = Client()
    user = User.objects.create_user(username='pushkar', password='coderslab')
    client.force_login(user)
    response = client.get(reverse('logout'))
    assert response.status_code == 302
    assert response.url == reverse('login')


@pytest.mark.django_db
def test_registration_view_invalid():
    client = Client()
    data = {
        'username': 'pushkar',
        'password1': 'coderslab',
        'password2': 'coderslab2020',
    }
    response = client.post(reverse('register'), data)
    assert response.status_code == 200
    assert not User.objects.filter(username='testuser').exists()


@pytest.mark.django_db
def test_registration_view_missing_fields():
    client = Client()
    data = {
        'username': '',
        'password1': 'newpassword',
        'password2': 'newpassword',
    }
    response = client.post(reverse('register'), data, follow=True)

    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == 'Error creating your account. Please correct the errors below.'
    assert not User.objects.filter(username='').exists()

    form = response.context['form']
    assert isinstance(form, RegistrationForm)
    assert form.errors
