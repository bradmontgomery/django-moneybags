#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from moneybags.models import Account
User = get_user_model()


class TestViews(TestCase):
    url = 'moneybags.urls'

    def setUp(self):

        # Create an (Un-)Authenticated clients
        self.ua_client = Client()

        # A Test User
        self.user = User.objects.create_user("testuser",
            email="testuser@example.com", password="sekrit")
        self.user.first_name = u"Tést"
        self.user.last_name = u"Üser"
        self.user.save()

        # Test User should be logged in to the default client
        assert self.client.login(username="testuser", password="sekrit")

    def tearDown(self):
        self.user.delete()

    def test_create_account_get(self):
        url = reverse("moneybags-create-account")

        # Unauthenticated reqeusts should redirect to login
        resp = self.ua_client.get(url)
        self.assertEqual(resp.status_code, 302)

        # Authenticated Get Requests should include a form
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "moneybags/create_account.html")
        self.assertIn('form', resp.context)

    def test_create_account_post(self):
        url = reverse("moneybags-create-account")

        # Prior to POSTing, no Accounts exist
        self.assertEqual(Account.objects.all().count(), 0)

        # POST
        data = {'name': 'Test Account'}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 302)

        # After POSTing, One Account exists
        self.assertEqual(Account.objects.all().count(), 1)

    def test_list_accounts(self):
        # Create an Account
        acct = Account.objects.create(name="Test Account", owner=self.user)

        url = reverse("moneybags-list-accounts")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "moneybags/list_accounts.html")
        self.assertIn("accounts", resp.context)
        self.assertIn(acct, resp.context['accounts'])
