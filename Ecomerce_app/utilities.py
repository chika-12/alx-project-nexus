import uuid
def uuid_verification(uuid_input):
  try:
    uuid.UUID(str(uuid_input))
  except ValueError:
    return False
  return True