import random

class NPCWeatherPreferences:
    def __init__(self, character_traits):
        self.weather_preferences = {
            '순수혈통': {
                'likes': ['맑음', '눈'],
                'dislikes': ['비', '습기'],
                'like_reactions': {
                    '맑음': ['우아하게 햇살을 만끽하며', '고상한 미소를 지으며'],
                    '눈': ['하얀 눈을 감상하며', '품위있게 눈길을 걸으며']
                },
                'dislike_reactions': {
                    '비': ['망토가 젖는 것을 싫어하며', '비에 젖은 머리카락을 불쾌하게 쓸어넘기며'],
                    '습기': ['불쾌한 듯 코를 찡그리며', '습한 공기에 짜증을 내며']
                },
                'speech_style': {
                    'good_mood': '거만하고 우아한',
                    'bad_mood': '짜증스럽고 거만한'
                }
            },
            '학구파': {
                'likes': ['비', '흐림'],
                'dislikes': ['천둥', '강풍'],
                'like_reactions': {
                    '비': ['창가에서 평화롭게 책을 읽으며', '빗소리를 들으며 집중하며'],
                    '흐림': ['조용한 분위기에 만족하며', '학습하기 좋은 날씨라며']
                },
                'dislike_reactions': {
                    '천둥': ['책에 집중하지 못하고 인상을 찌푸리며', '천둥소리에 펜을 떨어뜨리며'],
                    '강풍': ['날아다니는 양피지를 짜증스레 잡으며', '바람에 어지러워진 책상을 정리하며']
                },
                'speech_style': {
                    'good_mood': '논리적이고 차분한',
                    'bad_mood': '짜증스럽고 날카로운'
                }
            },
            '퀴디치선수': {
                'likes': ['맑음', '약한바람'],
                'dislikes': ['안개', '강풍', '비'],
                'like_reactions': {
                    '맑음': ['하늘을 향해 희망찬 미소를 지으며', '날기 좋은 날씨라며 신나하며'],
                    '약한바람': ['바람의 방향을 확인하며', '가벼운 바람을 즐기며']
                },
                'dislike_reactions': {
                    '안개': ['시야가 흐려 불만스러운 표정을 지으며', '안개 때문에 훈련을 포기하고'],
                    '강풍': ['빗자루가 흔들려 화난 표정으로', '위험한 바람에 불평하며'],
                    '비': ['젖은 퀴디치 장비를 털며 한숨쉬는', '미끄러운 빗자루를 걱정하며']
                },
                'speech_style': {
                    'good_mood': '활기차고 열정적인',
                    'bad_mood': '불만스럽고 답답한'
                }
            }
        }
        self.traits = character_traits

    def get_weather_reaction(self, weather):
        reaction = {
            'is_favorable': False,
            'mood_modifier': 0,
            'reaction': None,
            'speech_style': '일반적인'
        }
        
        for trait in self.traits:
            if trait in self.weather_preferences:
                prefs = self.weather_preferences[trait]
                
                if weather in prefs['likes']:
                    reaction['is_favorable'] = True
                    reaction['mood_modifier'] += 2
                    if weather in prefs['like_reactions']:
                        reaction['reaction'] = random.choice(prefs['like_reactions'][weather])
                    reaction['speech_style'] = prefs['speech_style']['good_mood']
                elif weather in prefs['dislikes']:
                    reaction['is_favorable'] = False
                    reaction['mood_modifier'] -= 2
                    if weather in prefs['dislike_reactions']:
                        reaction['reaction'] = random.choice(prefs['dislike_reactions'][weather])
                    reaction['speech_style'] = prefs['speech_style']['bad_mood']
        
        return reaction