import json
from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class DungeonMixin(LoginRequiredMixin):
    map_data = []

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        response = super().dispatch(request, *args, **kwargs)
        if isinstance(response, HttpResponseRedirect):
            return response
        with open(settings.BASE_DIR + request.user.dungeon.map.url, 'r', encoding='utf-8') as f:
            self.map_data = json.load(f)
        try:
            x = request.session.get('x', 0)
            y = request.session.get('y', 0)
            points = self.get_start_points()
            if (x == points[0] and y == points[1]) or\
                (x == 0 and y == 0):
                return response
            else:
                return redirect(self.get_point_reverse(x, y)) 
        except KeyError:
            pass
        return response

    def get_start_points(self) -> list[int]:
        for i in enumerate(self.map_data):
            for j in range(len(i[1])):
                if self.map_data[i[0]][j] == 2:
                    return [i[0], j]
        return [0, 2]

    def get_point_reverse(self, x: int, y: int) -> str:
        if x < 0 or y < 0:
            return None
        try:
            if self.map_data[x][y] == 1 or self.map_data[x][y] == 2:
                return reverse("dungeon") + f"?x={x}&y={y}"
            if self.map_data[x][y] == 4:
                return reverse("dungeon_enemy") + f"?x={x}&y={y}"
            if self.map_data[x][y] == 5:
                return reverse("dungeon_boss") + f"?x={x}&y={y}"
        except IndexError:
            pass
        return None