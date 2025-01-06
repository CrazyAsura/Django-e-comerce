from django import forms
from .models import User, Address, Phone

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'birth_date', 'cpf']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full py-3 pl-10 text-sm text-gray-700 border border-gray-300 rounded-xl my-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
                'placeholder': 'Nome'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full py-3 pl-10 text-sm text-gray-700 border border-gray-300 rounded-xl my-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
                'placeholder': 'E-mail'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'w-full py-3 pl-10 text-sm text-gray-700 border border-gray-300 rounded-xl my-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
                'placeholder': 'Senha'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'w-full py-3 pl-10 text-sm text-gray-700 border border-gray-300 rounded-xl my-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
                'placeholder': 'Data de Nascimento',
                'type': 'date'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'w-full py-3 pl-10 text-sm text-gray-700 border border-gray-300 rounded-xl my-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
                'placeholder': 'XXX.XXX.XXX-XX',
                'data-mask': '000.000.000-00'
            }),
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['zip_code', 'street', 'neighborhood', 'city', 'state']
        widgets = {
            'zip_code': forms.TextInput(attrs={
                'class': 'w-full py-3 pl-10 text-sm text-gray-700 border border-gray-300 rounded-xl my-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
                'placeholder': 'CEP',
                'data-mask': '00000-000'
            }),
            'street': forms.TextInput(attrs={
                'class': 'w-full py-3 pl-10 text-sm text-gray-700 border border-gray-300 rounded-xl my-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
                'placeholder': 'Rua'
            }),
            'neighborhood': forms.TextInput(attrs={
                'class': 'w-full py-3 pl-10 text-sm text-gray-700 border border-gray-300 rounded-xl my-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
                'placeholder': 'Bairro'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full py-3 pl-10 text-sm text-gray-700 border border-gray-300 rounded-xl my-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
                'placeholder': 'Cidade'
            }),
            'state': forms.Select(attrs={
                'class': 'w-full py-3 pl-10 text-sm text-gray-700 border border-gray-300 rounded-xl my-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
                'placeholder': 'Estado'
            }),
        }

class PhoneForm(forms.ModelForm):
    class Meta:
        model = Phone
        fields = ['number', 'type']
        widgets = {
            'number': forms.TextInput(attrs={
                'class': 'w-full py-3 pl-10 text-sm text-gray-700 border border-gray-300 rounded-xl my-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
                'placeholder': 'Número',
                'data-mask': '(00) 00000-0000'
            }),
            'type': forms.Select(attrs={
                'class': 'w-full py-3 pl-10 text-sm text-gray-700 border border-gray-300 rounded-xl my-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200'
            }),
        }
        
class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150, 
        label='CPF ou E-mail', 
        widget=forms.TextInput(attrs={
            'placeholder': 'CPF ou E-mail',
            'class': 'w-full py-3 pl-10 text-sm text-gray-700 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 shadow-sm hover:shadow-md',
            'data-mask': '000.000.000-00'
        })
    )
    password = forms.CharField(
        label='Senha', 
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Senha',
            'class': 'w-full py-3 pl-10 text-sm text-gray-700 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 shadow-sm hover:shadow-md',
        })
    )