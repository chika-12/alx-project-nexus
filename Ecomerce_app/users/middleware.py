import logging
logger = logging.getLogger("request_loggers")

class RequestLoggingMiddleware:
  """
    Middleware to log every incoming HTTP request
  """
  def __init__(self, get_response):
    self.get_response = get_response
  
  def __call__(self, request, *args, **kwds):
    
    try:
      body = request.body.decode('utf-8')
    except:
      body = "<unable to decode>"

    logger.info(
      f"Method: {request.method} | "
      f"Path: {request.get_full_path()} | "
      #f"Headers: {dict(request.headers)} | "
      #f"Body: {body}"
    )
    response = self.get_response(request)
    return response