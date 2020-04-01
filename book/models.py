from django.db import models
from django.urls import reverse

from accounts.models import User


class Category(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name']


class Book(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    author = models.CharField(max_length=50,null=True)
    information = models.CharField(max_length=200)
    total_stock = models.PositiveIntegerField(default=0)
    avail_stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return '(' + str(self.category) + ') ' + str(self.name)

    def get_absolute_url(self):
        return reverse('book:booklist')

class IssuedBook(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    issued_date = models.DateField()
    return_date = models.DateField()
    status = models.CharField(max_length=10, default='pending')

    def __str__(self):
        return str(self.id)+ ' ' + str(self.user.name) + '-' + str(self.book.name) + '(' + str(self.book.category.name) + ')-' + str(
            self.status)


class WaitingTable(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE)
    users = models.ManyToManyField(User,through='WaitingQueue')


class WaitingQueue(models.Model):
    users = models.ForeignKey(User, on_delete=models.CASCADE)
    waiting = models.ForeignKey(WaitingTable, on_delete=models.CASCADE)
    request_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.users.name) + ' (' + str(self.waiting.book.name)+ ') '+ str(self.request_time)