import random
from django.http import HttpRequest


class EffectMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if request.user.is_authenticated and request.user.enemy is None:
            if request.user.health >= 100:
                response = self.get_response(request)
                return response
            rand = random.randint(0,10)
            if rand + request.user.health > 100:
                request.user.health = 100
            else:
                request.user.health += rand
            request.user.save(update_fields=['health'])
            
        response = self.get_response(request)
        return response
