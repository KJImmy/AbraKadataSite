from rest_framework import serializers
from .models import Game
from .utils import add_game_from_link

class LinkSerializer(serializers.ModelSerializer):
	link = serializers.CharField(max_length=1000)
	team_details = serializers.JSONField(required=False)
	username = serializers.CharField(max_length=1000,required=False)

	class Meta:
		model = Game
		fields= ['link']

	def validate_link(self, value):
		# Make sure the link is to a PS replay
		if 'https://replay.pokemonshowdown.com/' not in value.lower():
			raise serializers.ValidationError("Not a valid replay link")
		return value

	def upload(self):
		# Needs to ensure that 2 users with extension don't upload game at same time
		link = self.validated_data['link']
		team_details = self.validated_data['team_details']
		username = self.validated_data['username']
		add_game_from_link(link,team_details,username)