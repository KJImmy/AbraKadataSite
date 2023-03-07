import requests

from games.models import Game

def validate_username(username,link1,link2):
	check1 = False
	check2 = False
	opponent1 = ""
	opponent2 = ""
	opponent_check = False
	final_check = False

	public_games = list(Game.objects.filter(public=True).values_list('link',flat=True))
	if link1[-4:] == ".log":
		link1 = link1[:-4]
	if link2[-4:] == ".log":
		link2 = link2[:-4]

	if link1 in public_games or link2 in public_games:
		return (final_check,"Please only submit private replays")

	if link1 == link2:
		return (final_check,"Please submit two distinct games")

	if link1[-4:] != ".log":
		link1+=".log"
	if link2[-4:] != ".log":
		link2+=".log"

	log1 = requests.get(link1).text
	log2 = requests.get(link2).text

	loopable_log1 = log1.split('\n')
	for line in loopable_log1:
		tokens = line.split('|')
		if len(tokens) < 2:
			continue
		if tokens[1] == "player" and len(tokens) > 3:
			print(tokens[3])
			if username == tokens[3]:
				check1 = True
			else:
				opponent1 = tokens[3]

	if not check1:
		return (final_check,"No matching username in game 1")

	loopable_log2 = log2.split('\n')
	for line in loopable_log2:
		tokens = line.split('|')
		if len(tokens) < 2:
			continue
		if tokens[1] == "player" and len(tokens) > 3:
			if username == tokens[3]:
				check2 = True
			else:
				opponent2 = tokens[3]

	if not check2:
		return (final_check,"No matching username in game 2")

	if opponent1 != opponent2:
		opponent_check = True

	if not opponent_check:
		return (final_check,"Please submit games against 2 distinct players")

	if check1 and check2 and opponent_check:
		final_check = True

	return (final_check,f"{username} is now connected to your account")