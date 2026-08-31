from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Account, Transaction
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.db import connection


def homePageView(request):
    return HttpResponse("""
        <h1>SecureBank</h1>

        <p>Welcome to SecureBank</p>

        <a href="/login/">Login</a>
    """)


def loginView(request):

    # VULNERABLE CODE - FLAW 5
    # if request.method == "POST":
    #     username = request.POST.get("username")
    #     password = request.POST.get("password")
    #
    #     user = authenticate(
    #         request,
    #         username=username,
    #         password=password
    #     )
    #
    #     if user is not None:
    #         login(request, user)
    #         return redirect("/dashboard/")
    #
    #     return HttpResponse("Invalid username or password")
    #
    # return render(request, "bank/login.html")

    # FIX
    if request.method == "POST":
        failed_attempts = request.session.get("failed_login_attempts", 0)

        if failed_attempts >= 5:
            return HttpResponse(
                "Too many failed login attempts. Please try again later."
            )

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            request.session.pop("failed_login_attempts", None)
            login(request, user)
            return redirect("/dashboard/")

        request.session["failed_login_attempts"] = failed_attempts + 1
        return HttpResponse("Invalid username or password")

    return render(request, "bank/login.html")


@login_required
def dashboardView(request):
    account = Account.objects.get(owner=request.user)

    return HttpResponse(f"""
        <h1>SecureBank Dashboard</h1>

        <p>Welcome, {request.user.username}</p>

        <p>Balance: ₹{account.balance}</p>

        <br>

        <a href="/transfer/">Transfer Money</a>

        <br><br>

        <a href="/logout/">Logout</a>
    """)


@login_required
def transferView(request):
    if request.method == "POST":
        receiver_username = request.POST.get("receiver")
        amount = request.POST.get("amount")
        description = request.POST.get("description", "")

        try:
            receiver = Account.objects.get(
                owner__username=receiver_username
            )
        except Account.DoesNotExist:
            return HttpResponse("Receiver account not found")

        if receiver.owner == request.user:
            return HttpResponse("You cannot transfer money to yourself")

        try:
            amount = Decimal(amount)
        except (TypeError, InvalidOperation):
            return HttpResponse("Invalid amount")

        if amount <= 0:
            return HttpResponse("Amount must be greater than zero")

        sender = Account.objects.get(owner=request.user)

        if amount > sender.balance:
            return HttpResponse("Insufficient balance")

        request.session["transfer_receiver"] = receiver_username
        request.session["transfer_amount"] = str(amount)
        request.session["transfer_description"] = description

        return redirect("/confirm/")

    return render(request, "bank/transfer.html")


@login_required
def confirmView(request):
    receiver_username = request.session.get("transfer_receiver")
    amount = request.session.get("transfer_amount")
    description = request.session.get("transfer_description", "")

    if not receiver_username or amount is None:
        return redirect("/transfer/")

    amount = Decimal(str(amount))

    if request.method == "POST":
        sender = Account.objects.get(owner=request.user)

        try:
            receiver = Account.objects.get(
                owner__username=receiver_username
            )
        except Account.DoesNotExist:
            return HttpResponse("Receiver account not found")

        if amount > sender.balance:
            return HttpResponse("Insufficient balance")

        with transaction.atomic():
            sender.balance -= amount
            receiver.balance += amount

            sender.save()
            receiver.save()

            Transaction.objects.create(
                sender=sender,
                receiver=receiver,
                amount=amount,
                description=description
            )

        request.session.pop("transfer_receiver", None)
        request.session.pop("transfer_amount", None)
        request.session.pop("transfer_description", None)

        return redirect("/dashboard/")

    return render(request, "bank/confirm.html", {
        "receiver": receiver_username,
        "amount": amount,
        "description": description
    })


def logoutView(request):
    logout(request)
    return redirect("/")

@login_required
def searchTransactionsView(request):

    # VULNERABLE CODE - FLAW 1
    # username = request.GET.get("username", "")
    #
    # with connection.cursor() as cursor:
    #     query = f"""
    #         SELECT *
    #         FROM bank_transaction
    #         WHERE sender_id IN (
    #             SELECT id FROM bank_account
    #             WHERE owner_id IN (
    #                 SELECT id FROM auth_user
    #                 WHERE username = '{username}'
    #             )
    #         )
    #         OR receiver_id IN (
    #             SELECT id FROM bank_account
    #             WHERE owner_id IN (
    #                 SELECT id FROM auth_user
    #                 WHERE username = '{username}'
    #             )
    #         )
    #     """
    #
    #     cursor.execute(query)
    #     transactions = cursor.fetchall()
    #
    # return HttpResponse(str(transactions))

    # FIX
    username = request.GET.get("username", "")

    with connection.cursor() as cursor:
        query = """
            SELECT *
            FROM bank_transaction
            WHERE sender_id IN (
                SELECT id FROM bank_account
                WHERE owner_id IN (
                    SELECT id FROM auth_user
                    WHERE username = ?
                )
            )
            OR receiver_id IN (
                SELECT id FROM bank_account
                WHERE owner_id IN (
                    SELECT id FROM auth_user
                    WHERE username = ?
                )
            )
        """

        cursor.execute(query, [username, username])
        transactions = cursor.fetchall()

    return HttpResponse(str(transactions))


@login_required
def accountView(request):

    # VULNERABLE CODE - FLAW 2
    # username = request.GET.get("username")
    #
    # try:
    #     account = Account.objects.get(owner__username=username)
    # except Account.DoesNotExist:
    #     return HttpResponse("Account not found")
    #
    # return HttpResponse(f"""
    #     <h1>Account Details</h1>
    #     <p>Username: {account.owner.username}</p>
    #     <p>Balance: ₹{account.balance}</p>
    # """)

    # FIX
    account = Account.objects.get(owner=request.user)

    return HttpResponse(f"""
        <h1>Account Details</h1>
        <p>Username: {account.owner.username}</p>
        <p>Balance: ₹{account.balance}</p>
    """)