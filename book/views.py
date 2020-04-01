from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.db.models import Q
from accounts.forms import RegistrationForm
from accounts.models import User
from .forms import BookRegistrationForm
from .models import Book, IssuedBook, WaitingTable, WaitingQueue
# Create your views here.
from django.views import View, generic
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
        if (IssuedBook.objects.filter(user=request.user, status__in=['booked', 'pending']).count() < 3) and \
                (IssuedBook.objects.filter(
                    Q(user=request.user) & Q(book=bookinput) & Q(status__in=['booked', 'pending'])).count() == 0) and \
                (WaitingQueue.objects.filter(users=request.user,
                                             waiting__book=bookinput).count() == 0):  # User can not issue more than 3 books & user can not issue same book again
            if bookinput.avail_stock > 0:
                # new req to the Issuedbook model if book is available in stock
                new_issue = IssuedBook.objects.create(book=bookinput, user=request.user,
                                                      issued_date=datetime.now().date(),
                                                      return_date=request.POST.get('date'))
                messages.info(request,
                              "Waiting for Librarian's Confirmation..You will be notified by email when its been approved..")
            else:
                waiting_obj, created = WaitingTable.objects.get_or_create(book=bookinput)
                waiting_list = waiting_obj.users.count() + 1
                waiting_obj.users.add(request.user)
                usr_list = ', '.join([usr.name for usr in waiting_obj.users.all()])
                messages.info(request,
                              "Waiting list is " + str(
                                  waiting_obj.users.count()) + ", users --> " + usr_list + ",You will be notified when book is available..")
        else:
            messages.error(request,
                           'You have already issued or request 3 books, return any book in order to issue another..')
            booklist = IssuedBook.objects.filter(user=request.user, status='booked')
            book_with_pending = IssuedBook.objects.filter(user=request.user, status='pending')
            return render(request, 'accounts/index.html',
                          {'booklist': booklist, 'book_with_pending': book_with_pending})
        return render(request, 'accounts/index.html')


class ApproveReq(View):
    """ for Librarian to accept req """

    @method_decorator(login_required, name='dispatch')
    def get(self, request):
        pending_req = IssuedBook.objects.filter(status='pending')
        return render(request, 'accounts/index.html', {'pending_req': pending_req})

    def post(self, request):
        req = IssuedBook.objects.get(book__id=request.POST.get('book'), user__id=request.POST.get('user_id'),
                                     status='pending')
        req.status = 'booked'
        req.save()
        book = Book.objects.get(id=request.POST.get('book'))
        book.avail_stock -= 1
        book.save()
        pending_req = IssuedBook.objects.filter(status='pending')
        messages.info(request, 'Approved book ' + str(req.book.name) + ' for user ' + str(req.user.name))
        return render(request, 'accounts/index.html', {'pending_req': pending_req})


class ReturnBook(View):

    @method_decorator(login_required, name='dispatch')
    def post(self, request):
        obj_del = IssuedBook.objects.filter(id=request.POST.get('entry_id'))
        # obj_del[0].delete()
        obj_del.first().delete()
        book = Book.objects.get(id=request.POST.get('book'))
        book.avail_stock += 1
        book.save()

        # book issue for first user in waiting model
        if book.avail_stock == 1 and WaitingTable.objects.filter(book=book).count() == 1:
            w = WaitingTable.objects.get(book=book)
            first_user = w.waitingqueue_set.all().order_by('request_time').first().users
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


class DeleteRequest(View):
    def post(self, request):
        del_obj = IssuedBook.objects.filter(book__id=int(request.POST.get('book_id')),
                                            user__id=int(request.POST.get('user_id')), status='pending')
        del_obj.delete()
        messages.success(request, 'Request deleted..')
        return redirect('book:approval')


class AllBookList(generic.ListView):
    template_name = 'book/booklist.html'
    paginate_by = 3

    def get_queryset(self):
        return Book.objects.all()


class MyRequestList(View):
    def get(self, request):
        reqlist = IssuedBook.objects.filter(user=request.user, status='pending')
        waiting_list = WaitingQueue.objects.filter(users=request.user)
        print(waiting_list)
        return render(request, 'book/myrequestlist.html', {'object_list': reqlist, 'Waiting_list': waiting_list})


class DeleteRequestUser(View):
    def post(self, request):
        del_obj = IssuedBook.objects.filter(book__id=int(request.POST.get('book_id')),
                                            user__id=int(request.POST.get('user_id')), status='pending')
        del_obj.delete()
        messages.success(request, 'Request deleted..')
        return redirect('book:reqlist')


class IssuedBooklist(View):
    def get(self, request):
        issued_book = IssuedBook.objects.filter(status='booked')
        return render(request, 'book/issuedbooklist.html', {'issued_book': issued_book})


class BookCreate(generic.CreateView):
    model = Book
    fields = '__all__'


class BookUpdate(generic.UpdateView):
    model = Book
    fields = '__all__'


class BookDelete(generic.DeleteView):
    model = Book
    success_url = reverse_lazy('book:booklist')


class WaitingReqDelete(View):
    def post(self, request):
        book = Book.objects.get(id=request.POST.get('book_id'))
        obj_del = WaitingQueue.objects.get(users=request.user).delete()
        w = WaitingTable.objects.get(book=book)
        if w.users.count() == 0:  # for last user in waitingtable..
            w.delete()
        messages.info(request,'Waiting request deleted..')
        return render(request, 'accounts/index.html')
