from tornado        import web
from tori.renderer  import DefaultRenderer, RendererService
from tori.exception import *

class Controller(web.RequestHandler):
    def render(self, template_name, **contexts):
        if not self._rendering_source:
            raise RenderingSourceMissingError, 'The source of template is not identified. This method is disabled.'
        
        if not self._rendering_engine:
            self._rendering_engine = DefaultRenderer
        
        output = None
        try:
            output = RendererService.instance().render(
                self._rendering_source,
                template_name,
                **contexts
            )
        except RendererNotFoundError:
            # When the renderer is not found. It is possible that the renderer is not yet
            # instantiated. This block of the code will do the lazy loading.
            renderer = self._rendering_engine(self._rendering_source)
            RendererService.instance().register(renderer).render(
                self._rendering_source,
                template_name,
                **contexts
            )
        
        self.write(output)
            
