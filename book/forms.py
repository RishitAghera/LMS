from django import forms

from book.models import Book


class BookRegistrationForm(forms.Form):

    class Meta:
        model = Book
        fields = ('name','author','information')