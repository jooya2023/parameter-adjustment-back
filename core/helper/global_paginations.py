from collections import OrderedDict

from django.conf import settings
from django.core.paginator import InvalidPage
from rest_framework import pagination
from rest_framework.exceptions import NotFound
from rest_framework.response import Response


# customizing pagination class
class CustomPagination(pagination.PageNumberPagination):
    page_size = int(settings.REST_FRAMEWORK['PAGE_SIZE'])
    max_page_size = int(settings.REST_FRAMEWORK['MAX_PAGE_SIZE'])
    page_query_param = 'p'
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('page_size', self.get_page_size(self.request)),
            ('results', data)
        ]))

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """

        page_number = request.GET.get('all')
        if page_number:
            return None
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)
