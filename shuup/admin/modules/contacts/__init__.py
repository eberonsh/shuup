# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import six
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from typing import Iterable

from shuup import configuration
from shuup.admin.base import AdminModule, MenuEntry, SearchResult
from shuup.admin.menu import CONTACTS_MENU_CATEGORY
from shuup.admin.utils.object_selector import get_object_selector_permission_name
from shuup.admin.utils.urls import admin_url, derive_model_url, get_model_url
from shuup.core.models import CompanyContact, Contact, PersonContact
from shuup.core.setting_keys import SHUUP_ENABLE_MULTIPLE_SHOPS, SHUUP_MANAGE_CONTACTS_PER_SHOP


class ContactModule(AdminModule):
    name = _("Contacts")
    breadcrumbs_menu_entry = MenuEntry(text=name, url="shuup_admin:contact.list", category=CONTACTS_MENU_CATEGORY)

    def get_urls(self):
        return [
            admin_url(
                r"^contacts/new/$",
                "shuup.admin.modules.contacts.views.ContactEditView",
                kwargs={"pk": None},
                name="contact.new",
            ),
            admin_url(
                r"^contacts/(?P<pk>\d+)/edit/$",
                "shuup.admin.modules.contacts.views.ContactEditView",
                name="contact.edit",
            ),
            admin_url(
                r"^contacts/(?P<pk>\d+)/$",
                "shuup.admin.modules.contacts.views.ContactDetailView",
                name="contact.detail",
            ),
            admin_url(
                r"^contacts/reset-password/(?P<pk>\d+)/$",
                "shuup.admin.modules.contacts.views.ContactResetPasswordView",
                name="contact.reset_password",
            ),
            admin_url(r"^contacts/$", "shuup.admin.modules.contacts.views.ContactListView", name="contact.list"),
            admin_url(
                r"^contacts/list-settings/",
                "shuup.admin.modules.settings.views.ListSettingsView",
                name="contact.list_settings",
            ),
            admin_url(
                r"^contacts/mass-edit/$",
                "shuup.admin.modules.contacts.views.ContactMassEditView",
                name="contact.mass_edit",
            ),
            admin_url(
                r"^contacts/mass-edit-group/$",
                "shuup.admin.modules.contacts.views.ContactGroupMassEditView",
                name="contact.mass_edit_group",
            ),
        ]

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=_("Contacts"),
                icon="fa fa-users",
                url="shuup_admin:contact.list",
                category=CONTACTS_MENU_CATEGORY,
                ordering=1,
            )
        ]

    def get_search_results(self, request, query):
        minimum_query_length = 3
        if len(query) >= minimum_query_length:
            filters = Q(Q(name__icontains=query) | Q(email=query))

            # show only contacts which the shop has access
            if configuration.get(None, SHUUP_ENABLE_MULTIPLE_SHOPS) and configuration.get(
                None, SHUUP_MANAGE_CONTACTS_PER_SHOP
            ):
                filters &= Q(shops=request.shop)

            if not request.user.is_superuser:
                filters &= ~Q(PersonContact___user__is_superuser=True)

            contacts = Contact.objects.filter(filters)
            for i, contact in enumerate(contacts[:10]):
                relevance = 100 - i
                yield SearchResult(
                    text=six.text_type(contact), url=get_model_url(contact), category=_("Contacts"), relevance=relevance
                )

    def get_model_url(self, object, kind, shop=None):
        return derive_model_url(Contact, "shuup_admin:contact", object, kind)

    def get_extra_permissions(self) -> Iterable[str]:
        return [
            get_object_selector_permission_name(Contact),
            get_object_selector_permission_name(PersonContact),
            get_object_selector_permission_name(CompanyContact),
        ]

    def get_permissions_help_texts(self) -> Iterable[str]:
        return {
            get_object_selector_permission_name(Contact): _("Allow the user to select contacts in admin."),
            get_object_selector_permission_name(PersonContact): _("Allow the user to select person contacts in admin."),
            get_object_selector_permission_name(CompanyContact): _(
                "Allow the user to select company contacts in admin."
            ),
        }
