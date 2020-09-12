import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1

# https://docs.gunicorn.org/en/stable/settings.html#access-log-format
access_log_format = "%(t)s %(h)s %(a)s %(m)s %(U)s %(s)s %(L)ss %(b)sB"
accesslog = "-"  # Log to stdout == CloudWatch
loglevel = "info"
