from rest_framework.renderers import BrowsableAPIRenderer

class AssignmentAPI(BrowsableAPIRenderer):
    template = 'api.html'

    def get_context_data(self, *agrs, **kwagrs):
        context = super().get_context_data(*args, **kwargs)
        context['content'] = self.response.content
        return context