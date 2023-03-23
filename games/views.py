from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from .models import Game
from .serializers import LinkSerializer

@api_view(['POST'])
def link_submission(request):
	if request.method == 'POST':
		data = JSONParser().parse(request)
		serializer = LinkSerializer(data=data)
		if serializer.is_valid():
			serializer.upload()
			return JsonResponse(serializer.data,status=201)
		return JsonResponse(serializer.errors,status=400)