RESET_DATA_TYPES = ['contacts', 'address', 'documents']
RESET_DATA_SUBTYPES = ['phone', 'email', 'house_number',
                       'street', 'zip_code', 'city', 'state', 'country']


def invalidate_step(signup, step):
    invalidated_steps = signup.get_invalidated_steps()
    if step not in invalidated_steps:
        invalidated_steps.append(step)
    signup.invalidated_steps = ','.join(invalidated_steps)
    signup.save()


def reset_address(signup, fields):
    address = signup.addresses.get(address_type='user_input')
    if 'house_number' in fields:
        address.house_number = ''
    if 'street' in fields:
        address.street = ''
    if 'zip_code' in fields:
        address.zip_code = ''
    if 'city' in fields:
        address.city = ''
    if 'state' in fields:
        address.state = ''
    if 'country' in fields:
        address.country = ''
    address.save()
    invalidate_step(signup, '0')


def reset_signup_form(signup, reset_data):
    if 'address' in reset_data['data_types']:
        reset_address(signup, reset_data['data_subtypes'])
    if 'contacts' in reset_data['data_types']:
        if 'email' in reset_data['data_subtypes']:
            invalidate_step(signup, '1')
        if 'phone' in reset_data['data_subtypes']:
            invalidate_step(signup, '2')
    if 'documents' in reset_data['data_types']:
        signup.photo = None
        signup.save()
        invalidate_step(signup, '3')
