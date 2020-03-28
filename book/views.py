from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator

from .models import Book, IssuedBook, WaitingTable
# Create your views here.
from django.views import View
import json
from datetime import datetime, timedelta


def autocompleteModel(request):
    """searchbar autocomplete"""
    if request.is_ajax():
        q = request.GET.get('term')
        search_qs = Book.objects.filter(name__istartswith=q)
        results = []
        for r in search_qs:
            results.append(r.name)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


class BookSearch(View):
    """provides list of all book for search """

    @method_decorator(login_required, name='dispatch')
    def get(self, request):
        return render(request, 'book/book_search.html')

    def post(self, request):
        bookinput = request.POST.get('bookinput').strip()
        searchresult = Book.objects.all().filter(name__iexact=bookinput)
        return render(request, 'book/book_search.html', {'searchresult': searchresult})


class MyIssuedBook(View):
    """ book issue request and user's book list"""

    @method_decorator(login_required, name='dispatch')
    def get(self, request):
        booklist = IssuedBook.objects.filter(user=request.user, status='booked')
        return render(request, 'accounts/index.html', {'booklist': booklist})

    def post(self, request):
        data = request.POST.copy()
        bookinput = Book.objects.get(id=data.get('book'))
        if IssuedBook.objects.filter(user=request.user,
                                     status='booked').count() < 3:  # User can not issue more than 3 books
            if bookinput.avail_stock > 0:
                # new req to the Issuedbook model if book is available in stock
                new_issue = IssuedBook.objects.create(book=bookinput, user=request.user,
                                                      issued_date=datetime.now().date(),
                                                      return_date=request.POST.get('date'))
                messages.info(request,
                              "Waiting for Librarian's Confirmation..You will be notified by email when its been approved")
            else:
                # when no stock available then new entry in waitingtable.
                if WaitingTable.objects.filter(book=bookinput).count() == 0:
                    new_waiting = WaitingTable.objects.create(book=bookinput)
                    waiting_list = new_waiting.users.count() + 1
                    new_waiting.users.add(request.user)
                else:
                    waiting_entry = WaitingTable.objects.get(book=bookinput)
                    waiting_list = waiting_entry.users.count() + 1
                    waiting_entry.users.add(request.user)
                messages.info(request,
                              'Waiting list is ' + str(waiting_list) + ',You will be notified when book is available..')
        else:
            messages.error(request, 'You have already issued 3 books, return any book in order to issue another..')
            booklist = IssuedBook.objects.filter(user=request.user, status='booked')
            return render(request, 'accounts/index.html', {'booklist': booklist})
        return render(request, 'accounts/index.html')


class ApproveReq(View):
    """ for Librarian to accept req """

    @method_decorator(login_required, name='dispatch')
    def get(self, request):
        pending_req = IssuedBook.objects.filter(status='pending')
        return render(request, 'accounts/index.html', {'pending_req': pending_req})

    def post(self, request):
        print(request.POST.get('book'))
        req = IssuedBook.objects.get(book__id=request.POST.get('book'), user__id=request.POST.get('user_id'))
        req.status = 'booked'
        req.save()
        print('updated')
        pending_req = IssuedBook.objects.filter(status='pending')
        messages.info(request, 'Approved book ' + str(req.book.name) + ' for user ' + str(req.user.name))
        return render(request, 'accounts/index.html', {'pending_req': pending_req})


class ReturnBook(View):

    @method_decorator(login_required, name='dispatch')
    def post(self, request):
        print(request.POST.get('entry_id'))
        obj_del = IssuedBook.objects.filter(id=request.POST.get('entry_id'))
        print(obj_del)
        obj_del[0].delete()
        book = Book.objects.get(id=request.POST.get('book'))
        book.avail_stock += 1
        book.save()

        # book issue for first user in waiting model
        print('count in waitingtable:' + str(WaitingTable.objects.filter(book=book).count()))
        if book.avail_stock == 1 and WaitingTable.objects.filter(book=book).count() == 1:
            w = WaitingTable.objects.get(book=book)
            print('w=' + str(w))
            first_user = w.waitingqueue_set.all().order_by('request_time').first().users
            print(first_user)
            new_issue = IssuedBook.objects.create(book=book, user=first_user,
                                                  issued_date=datetime.now().date(),
                                                  return_date=datetime.now().date() + timedelta(days=5))
            w.users.remove(first_user)
            w.save()
            if w.users.count() == 0:  # for last user in waitingtable..
                w.remove()
                w.save()

        messages.info(request, 'Book is returned')
        booklist = IssuedBook.objects.filter(user=request.user, status='booked')
        return render(request, 'accounts/index.html', {'booklist': booklist})
