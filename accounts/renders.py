from rest_framework.renderers import BrowsableAPIRenderer

class AccountAPI(BrowsableAPIRenderer):
    template = 'api.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['content'] = self.response.content
        return context