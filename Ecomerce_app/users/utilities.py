# requiredFields = ['phone_number', 'profile_photo', 'state', 'city', 'address']
# def selectRequiredFields(field):
#   for key in list(field.keys()):
#     if key not in requiredFields:
#       field.pop(key, None)
#   return field


def selectRequiredFields(field):
  required = {}
  for key in ['phone_number', 'state', 'city', 'address']:
    if key in field:
      required[key] = field[key]
    # Do NOT remove 'profile_photo'; leave it in request.data
    return {**required, 'profile_photo': field.get('profile_photo', None)}
