from weather_forecast import WeatherForecast
from npc_weather_preferences import NPCWeatherPreferences
import random
from datetime import datetime

class NPCBehaviorSystem:
    WEATHER_EFFECTS = {
        '비': {
            'mood_modifier': -1,  # 약간 우울한 분위기
            'locations': ['도서관', '기숙사', '교실'],  # 실내 선호
            'actions': {
                '도서관': ['책을 읽으며 창밖의 빗소리를 듣는', '비를 피해 도서관에서 공부하는'],
                '기숙사': ['창가에서 빗방울을 세며 멍하니 있는', '따뜻한 차를 마시며 휴식을 취하는'],
                '교실': ['젖은 망토를 털며 교실에 들어서는', '창밖의 비를 구경하며 수업을 듣는']
            },
            'dialogue_style': '조용하고 차분한',
            'topics': ['비 오는 날의 운치', '실내 활동', '따뜻한 음료']
        },
        '맑음': {
            'mood_modifier': 2,  # 매우 긍정적
            'locations': ['퀴디치 경기장', '호수가', '정원'],
            'actions': {
                '퀴디치 경기장': ['빗자루를 들고 신나게 날아다니는', '경기장에서 연습하는'],
                '호수가': ['호수가에서 친구들과 담소를 나누는', '나무 그늘에서 쉬고 있는'],
                '정원': ['허브를 채집하는', '마법 생물들을 관찰하는']
            },
            'dialogue_style': '활기차고 밝은',
            'topics': ['퀴디치', '야외 활동', '마법 생물']
        },
        '흐림': {
            'mood_modifier': 0,  # 중립적
            'locations': ['도서관', '교실', '정원'],
            'actions': {
                '도서관': ['창가에서 책을 읽는', '과제를 하는'],
                '교실': ['수업에 집중하는', '필기를 하는'],
                '정원': ['산책하는', '약초를 관찰하는']
            },
            'dialogue_style': '평온한',
            'topics': ['수업', '일상적인 대화', '과제']
        },
        '천둥': {
            'mood_modifier': -2,  # 매우 불안
            'locations': ['기숙사', '도서관', '지하 던전'],
            'actions': {
                '기숙사': ['이불 속에 숨어있는', '창문을 걱정스레 바라보는'],
                '도서관': ['책 더미 뒤에 숨어있는', '천둥 소리에 움찔거리는'],
                '지하 던전': ['안전한 곳을 찾아 숨어있는', '불안한 듯 주변을 살피는']
            },
            'dialogue_style': '긴장되고 불안한',
            'topics': ['날씨의 위험성', '실내 대피', '안전']
        },
        '바람': {
            'mood_modifier': -1,  # 약간 불안정
            'locations': ['실내', '복도', '기숙사'],
            'actions': {
                '실내': ['망토를 단단히 여미는', '흐트러진 머리를 매만지는'],
                '복도': ['바람에 날리는 양피지를 잡으려 뛰어다니는', '창문을 조심스레 닫는'],
                '기숙사': ['창밖의 바람 소리를 듣는', '따뜻한 곳을 찾아 움츠리는']
            },
            'dialogue_style': '산만하고 불안정한',
            'topics': ['강한 바람', '실내 활동', '날씨 주의사항']
        },
        '습기': {
            'mood_modifier': -1,  # 약간 불쾌
            'locations': ['도서관', '교실', '지하 던전'],
            'actions': {
                '도서관': ['책의 습기를 걱정하며 확인하는', '제습 마법을 시전하는'],
                '교실': ['불쾌한 듯 옷매무새를 고치는', '머리를 계속 만지작거리는'],
                '지하 던전': ['축축한 벽을 피해 다니는', '마법약 재료를 점검하는']
            },
            'dialogue_style': '짜증스럽고 불편한',
            'topics': ['습한 날씨', '곰팡이 방지', '컨디션']
        },
        '안개': {
            'mood_modifier': -1,  # 약간 신비로움
            'locations': ['실내', '복도', '교실'],
            'actions': {
                '실내': ['창밖의 안개를 멍하니 바라보는', '방향 지시 마법을 확인하는'],
                '복도': ['안개 속을 조심스레 걷는', '지팡이 빛을 밝히는'],
                '교실': ['안개 낀 창밖을 자주 바라보는', '집중하려 노력하는']
            },
            'dialogue_style': '신비롭고 조심스러운',
            'topics': ['안개 속 풍경', '방향 찾기', '신비한 분위기']
        },
        '추위': {
            'mood_modifier': -1,  # 약간 움츠러듦
            'locations': ['기숙사', '도서관', '식당'],
            'actions': {
                '기숙사': ['벽난로 앞에서 몸을 녹이는', '담요를 두르고 있는'],
                '도서관': ['따뜻한 차를 마시며 공부하는', '장갑을 낀 채 책장을 넘기는'],
                '식당': ['뜨거운 수프를 먹는', '따뜻한 음료를 마시는']
            },
            'dialogue_style': '떨리는 듯한',
            'topics': ['추위', '따뜻한 음식', '보온 마법']
        },
        '눈': {
            'mood_modifier': 1,  # 긍정적
            'locations': ['창가', '정원', '기숙사'],
            'actions': {
                '창가': ['눈 내리는 풍경을 감상하는', '창문에 낙서하는'],
                '정원': ['눈사람을 만드는', '눈싸움을 하는'],
                '기숙사': ['따뜻한 버터맥주를 마시는', '벽난로 앞에서 이야기하는']
            },
            'dialogue_style': '즐겁고 들뜬',
            'topics': ['눈놀이', '겨울 풍경', '따뜻한 음료']
        }
    }

    def __init__(self, current_weather):
        self.current_weather = current_weather
        self.weather_effect = self.WEATHER_EFFECTS[current_weather]
        self.weather_prefs = NPCWeatherPreferences([])

    def generate_dialogue(self, character_info, behavior):
        """날씨와 성격을 반영한 대화 생성"""
        mood = behavior['mood']
        style = behavior['dialogue_style']
        personality = character_info['personality']
        
        # 날씨와 감정에 따른 대사 생성
        dialogue_templates = {
            '비': {
                'good_mood': [
                    "비 오는 날의 도서관은 더욱 운치있지 않나요?",
                    "이런 날씨엔 따뜻한 버터맥주가 생각나네요.",
                    "빗소리를 들으며 공부하는 게 집중이 더 잘되는 것 같아요."
                ],
                'bad_mood': [
                    "이런 날씨는 정말 견딜 수가 없어요.",
                    "망토가 다 젖잖아요! 최악이에요.",
                    "비가 그치기 전까진 밖에 나가고 싶지 않네요."
                ]
            },
            '맑음': {
                'good_mood': [
                    "이런 날씨에 퀴디치 연습이 없다니 아쉽네요!",
                    "호그와트의 맑은 하늘은 언제 봐도 아름다워요.",
                    "밖에서 마법 생물 수업하기 딱 좋은 날씨예요."
                ],
                'bad_mood': [
                    "햇빛이 너무 강해서 눈이 부셔요.",
                    "이런 날씨에도 실내에서 공부해야 한다니...",
                    "날이 너무 좋아서 오히려 집중이 안되네요."
                ]
            }
        }

        # 날씨와 기분에 따른 대사 선택
        weather_templates = dialogue_templates.get(self.current_weather, {
            'good_mood': ["오늘도 평화로운 하루네요."],
            'bad_mood': ["흠... 그저 그런 날이에요."]
        })
        
        mood_key = 'good_mood' if mood > 0 else 'bad_mood'
        dialogue = random.choice(weather_templates[mood_key])

        # 캐릭터의 성격에 따른 대사 수정
        if '거만' in personality:
            dialogue = dialogue.replace("요", "군").replace("네요", "는군")
        elif '수줍' in personality:
            dialogue = dialogue.replace("요", "요...").replace("!", "...")
        
        return f"({behavior['action']}) \"{dialogue}\""

    def generate_npc_behavior(self, character_info):
        # 날씨 선호도 확인
        self.weather_prefs = NPCWeatherPreferences(character_info['traits'])
        weather_reaction = self.weather_prefs.get_weather_reaction(self.current_weather)
        
        # 위치와 행동 선택
        location = random.choice(self.weather_effect['locations'])
        action = weather_reaction['reaction'] if weather_reaction['reaction'] else \
                random.choice(self.weather_effect['actions'][location])
        
        # 감정 상태 계산
        mood = character_info.get('base_mood', 0) + \
               self.weather_effect['mood_modifier'] + \
               weather_reaction['mood_modifier']
        
        behavior = {
            'location': location,
            'action': action,
            'mood': mood,
            'dialogue_style': weather_reaction['speech_style']
        }
        
        return behavior

    def format_npc_response(self, character_info, behavior):
        """최종 NPC 응답 형식화"""
        return self.generate_dialogue(character_info, behavior)

def example_usage():
    # 현재 날씨 가져오기
    weather_system = WeatherForecast()
    current_weather = weather_system.post_daily_forecast()

    # NPC 행동 시스템 초기화
    npc_system = NPCBehaviorSystem(current_weather)

    # 캐릭터 정보 예시
    character_info = {
        'name': '루나 러브굿',
        'base_mood': 1,  # 기본적으로 긍정적인 성격
        'personality': '몽환적이고 독특한',
        'usual_topics': ['신비한 생물', '이상한 이론', '래번클로']
    }

    # NPC 행동 및 대화 생성
    behavior = npc_system.generate_npc_behavior(character_info)
    response = npc_system.format_npc_response(character_info, behavior)
    
    print(response)





















