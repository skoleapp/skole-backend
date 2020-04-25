from django.http import HttpRequest, HttpResponse


def health_check(request: HttpRequest) -> HttpResponse:
    """AWS ELB will poll this periodically. This can have as much logic as possible,
    any status other than 200 is considered a failure.
    """
    return HttpResponse(status=200)
