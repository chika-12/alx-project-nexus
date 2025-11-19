requiredFields = ['phone_number', 'profile_photo', 'state', 'city', 'address']
def selectRequiredFields(field):
  for key in list(field.keys()):
    if key not in requiredFields:
      field.pop(key, None)
  return field

