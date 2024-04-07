import os
from .models import *
from uuid import uuid1


def upload_image_base64(file_data):
    if not file_data.content_type.startswith('image'):
        return False, None

    extn = os.path.splitext(file_data.name)[1]
    filename = str(uuid1()) + extn
    path = os.path.join('media/avatar/', filename)
    with open(path, 'wb') as destination:
        for chunk in file_data.chunks():
            destination.write(chunk)

    return True, path

def check_admin_status(username):
    m = Profile.objects.filter(soft_delete=False,
                                    user__username__exact=username)
    if len(m):
        m = m[0]
        return m.user,True
    else:
        return None,False

