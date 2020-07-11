def user_is_member(request):
    club_id=request.path.split('/')[2]
    return request.user.is_member(club_id)


def user_is_ec(request):
    club_id=request.path.split('/')[2]
    return request.user.is_ec(club_id)

