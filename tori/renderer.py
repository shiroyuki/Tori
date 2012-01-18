from jinja2 import Template

class TemplateRepositoryNotExisted(Exception):
    '''
    This is an exception when the targeted template repository does not exist.
    '''

class RendererNotImplemented(Exception):
    '''
    This is an exception when the renderer is not fully implemented according to the requirement.
    '''

class TemplateRepository(unicode):
    def __init__(self, name, location):
        '''
        Template repository
        
        `name` is the name of the repository.

        `location` is the location of the repository.
        '''
        self.name = name
        self.location = location

    def __str__(self):
        return self.location

class TemplateRepositoryManager(dict):
    def register(self, repository):
        '''
        Register the repository.
        
        `repository` is an instance of TemplateRepository.
        '''
        self[repository.name] = repository
        return self

    def disown(self, name):
        '''
        Disown the repository.

        `name` is the name of the repository.
        '''
        if not self[name]:
            raise TemplateRepositoryNotExisted, "Cannot get the repository."
        del self[name]
        return self

    def get(self, name):
        '''
        Get a repository by name.

        `name` is the name of the requested repository.
        '''
        if not self[name]:
            raise TemplateRepositoryNotExisted, "Cannot get the repository."
        return self[name]

class RenderingService(object):
    __repositories = TemplateRepository()
    __renderer = None

    def __init__(self, renderer, *args, **kwargs):
        '''
        Rendering service in case that extra renderers are required.

        `renderer` is a reference to a Renderer-type class. It should not be an instance.
        '''
        self.__renderer = renderer

    def repositories(self):
        '''
        Get the repository manager.
        '''
        return self.__repositories

    def render(self, repository_name, template_name, **context_variables):
        '''
        Render a template. (wrapper)

        `repository_name` is the name of the targeted repository.

        `template_name` is the name of the template.

        `context_variables` is the dictionary containing context variables necessary for rendering.
        '''
        repository = self.repositories().get(repository_name)
        return self.__renderer.render(repository, template_name, **context_variables);

class Renderer(object):
    def __init__(self):
        '''
        The basic renderer as a template for implementing a compatible renderer.
        '''
        pass

    def render(self, repository, template_name, **context_variables):
        '''
        Render a template. (overriding required)

        `repository` is the targeted repository.

        `template_name` is the name of the template.

        `context_variables` is the dictionary containing context variables necessary for rendering.
        '''
        raise RendererNotImplemented, "Renderer does not know how to render the template."

