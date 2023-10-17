from expoptapi.api.backend.ws.profile import ExpertProfile

class EoApi:
    def __init__(self, token: str):
        self.token = token
    async def Profile(self):
        profile = ExpertProfile()
        ProfileData = await profile.get(token=self.token)
        return ProfileData