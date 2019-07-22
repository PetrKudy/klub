from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserChangeForm, UserCreationForm
from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .models import AdministrativeUnit, UserProfile
from .views import get_unique_username


def username_validation(user, fields):
    if user.username == '':
        user.username = get_unique_username(fields['email'])
    else:
        user.username = fields['username']


class UserFormMixin(object):
    def clean(self):
        try:
            user = UserProfile.objects.get(email=self.cleaned_data['email'])
            administrated_unit = AdministrativeUnit.objects.get(id=self.request.user.administrated_units.all()[0].id)
            user.administrative_units.add(administrated_unit)
            user.save()
            url = reverse('admin:aklub_userprofile_change', args=(user.pk,))
            self.add_error(
                'email',
                mark_safe(
                    _(f'<a href="{url}">User with this email already exist in database and is available now, click here to edit</a>'),
                ),
            )
            return super(UserFormMixin, self).clean()
        except UserProfile.DoesNotExist:
            return super(UserFormMixin, self).clean()


class UserCreateForm(UserFormMixin, UserCreationForm):
    password = ReadOnlyPasswordHashField()

    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['username'].required = False
        self.fields['password'].help_text = 'You can set password in the next step or anytime in user detail form'

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.username = self.cleaned_data['username']
        username_validation(user=user, fields=self.cleaned_data)

        if commit:
            user.save()
        return user


class UserUpdateForm(UserChangeForm):
    password = ReadOnlyPasswordHashField()

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields['username'].required = False
        self.fields['password'].help_text = (
            "Raw passwords are not stored, so there is no way to see "
            "this user's password, but you can <a href=\"%s\"> "
            "<strong>Change the Password</strong> using this form</a>."
                                            ) % reverse_lazy(
            'admin:auth_user_password_change',
            args=[self.instance.id],
        )

    def save(self, commit=True):
        user = super(UserChangeForm, self).save(commit=False)
        user.username = self.cleaned_data['username']
        username_validation(user=user, fields=self.cleaned_data)

        if commit:
            user.save()
        return user
