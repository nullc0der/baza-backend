RESET_DATA_TYPES = ['contacts', 'address', 'documents']
RESET_DATA_SUBTYPES = ['phone', 'email', 'house_number',
                       'street', 'zip_code', 'city', 'state', 'country']


def invalidate_step_and_fields(signup, step, fields):
    invalidated_steps = signup.get_invalidated_steps()
    invalidated_fields = signup.get_invalidated_fields()
    if step not in invalidated_steps:
        invalidated_steps.append(step)
    for field in fields:
        if field not in invalidated_fields:
            invalidated_fields.append(field)
    signup.invalidated_steps = ','.join(invalidated_steps)
    signup.invalidated_fields = ','.join(invalidated_fields)
    signup.save()


def reset_address(signup, fields):
    address = signup.addresses.get(address_type='user_input')
    fields_to_invalidate = []
    if 'house_number' in fields:
        address.house_number = ''
        fields_to_invalidate.append('house_number')
    if 'street' in fields:
        address.street = ''
        fields_to_invalidate.append('street')
    if 'zip_code' in fields:
        address.zip_code = ''
        fields_to_invalidate.append('zip_code')
    if 'city' in fields:
        address.city = ''
        fields_to_invalidate.append('city')
    if 'state' in fields:
        address.state = ''
        fields_to_invalidate.append('state')
    if 'country' in fields:
        address.country = ''
        fields_to_invalidate.append('country')
    address.save()
    invalidate_step_and_fields(signup, '0', fields_to_invalidate)


def reset_signup_form(signup, reset_data):
    if 'address' in reset_data['data_types']:
        reset_address(signup, reset_data['data_subtypes'])
    if 'contacts' in reset_data['data_types']:
        if 'email' in reset_data['data_subtypes']:
            invalidate_step_and_fields(signup, '1', ['email'])
        if 'phone' in reset_data['data_subtypes']:
            invalidate_step_and_fields(signup, '2', ['phone'])
    if 'documents' in reset_data['data_types']:
        invalidate_step_and_fields(signup, '3', [])
    additional_info = signup.bazasignupadditionalinfo
    additional_info.invalidation_comment = reset_data.get(
        'invalidation_comment', '')
    additional_info.save()
