from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math

class CustomPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'pagesize'
    max_page_size = 100

    def get_page_size(self, request):
        pagesize = request.query_params.get(self.page_size_query_param)
        if not pagesize:
            self.page_size = None
            raise Exception("'pagesize' is required")
        return super().get_page_size(request)

    # def get_paginated_response(self, data):
    #     return Response({
    #         'total': self.page.paginator.count,
    #         'total_pages': math.ceil(self.page.paginator.count / self.get_page_size(self.request)),
    #         'page': self.page.number,
    #         'pagesize': self.get_page_size(self.request),
    #         'results': data
    #     })

