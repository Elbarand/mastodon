import schedule
import time
import random
from mastodon import Mastodon
from datetime import datetime

class WeatherCasterBot:
    def __init__(self, mastodon_client):
        self.mastodon = mastodon_client
        self.weather_types = ['맑음', '비', '안개', '눈', '바람', '추위']
        self.weather_caster = {
            'name': '루나 스카이',
            'title': '마법기상청 기상캐스터'
        }
        
        self.weather_messages = {
            '맑음': [
                "안녕하세요! {name}입니다. 오늘 호그와트는 화창한 날씨가 예상됩니다! ☀️ 퀴디치 연습하기 딱 좋은 날이 될 것 같네요!",
                "여러분, 좋은 아침입니다. {name}의 일기예보입니다. 오늘은 맑은 하늘이 종일 이어질 예정이에요. 수업 중 창밖 구경하기 좋은 날씨가 되겠습니다! ✨",
                "마법기상청에서 전해드립니다! 오늘은 맑은 날씨로, 호그와트 성 위로 아름다운 파란 하늘이 펼쳐질 예정입니다. 야외 수업하기 정말 좋은 날이에요! 🌞"
            ],
            '비': [
                "{name}입니다. 오늘은 비가 내릴 예정이에요. 🌧️ 방수 마법을 미리 준비하시는 것을 추천드립니다!",
                "안녕하세요, {name}의 일기예보입니다. 오늘은 종일 비가 내릴 것으로 보입니다. 우산 마법을 잊지 마세요! ☔",
                "마법기상청 특보입니다! 비 소식이에요. 도서관에서 책과 함께하기 좋은 날씨가 되겠습니다. 빗소리를 들으며 공부해보는 건 어떨까요? 🎧"
            ],
            '안개': [
                "여러분, {name}입니다. 오늘은 짙은 안개가 예상됩니다. 🌫️ 루모스 마법을 준비해주세요!",
                "마법기상청 {name}입니다. 오늘 호그와트 주변은 신비로운 안개가 가득할 예정이에요. 이동 시 주의가 필요합니다! 🌫️",
                "안개 주의보! {name}이 전해드립니다. 오늘은 방향 지시 마법을 꼭 확인하고 다니세요. 금지된 숲 주변은 특히 조심! 🎯"
            ],
            '눈': [
                "마법기상청 {name}입니다! 오늘은 아름다운 눈이 내릴 예정이에요. ❄️ 따뜻한 망토를 준비해주세요!",
                "안녕하세요, {name}입니다. 호그와트에 눈이 내립니다! 눈사람 마법 연습하기 좋은 날이 되겠어요. ⛄",
                "눈 소식을 전해드립니다! 오늘은 호그와트 전역에 함박눈이 예상됩니다. 미끄럼 방지 마법을 잊지 마세요! 🎿"
            ],
            '바람': [
                "{name}입니다. 오늘은 강한 바람이 예상됩니다. 💨 빗자루 비행 시 특별한 주의가 필요해요!",
                "마법기상청 특보! 강풍이 예상됩니다. 날아다니는 물체들을 주의하시고, 고정 마법을 활용해주세요! 🌪️",
                "바람이 매우 강할 예정입니다. 퀴디치 연습은 실내에서 이론 수업으로 대체하시는 것을 추천드려요! 🏰"
            ],
            '추위': [
                "추운 날씨가 예상됩니다! {name}이 알려드리는 오늘의 팁: 따뜻한 버터맥주 한 잔 어떠신가요? ❄️",
                "마법기상청 {name}입니다. 오늘은 매서운 추위가 예상됩니다. 온열 마법을 미리 준비해주세요! 🧣",
                "추위 주의보! 벽난로 근처 자리는 일찍 차지하시는 게 좋을 것 같아요! 따뜻한 코코아로 하루를 시작해보세요. ☕"
            ]
        }

    def get_daily_weather(self):
        """오늘의 날씨를 랜덤으로 선택"""
        return random.choice(self.weather_types)

    def post_daily_weather(self):
        """날씨 예보 포스팅"""
        weather = self.get_daily_weather()
        message = random.choice(self.weather_messages[weather])
        
        # 기상캐스터 이름 포맷팅
        message = message.format(name=self.weather_caster['name'])
        
        # 날짜 추가
        today = datetime.now().strftime("%Y년 %m월 %d일")
        full_message = f"""
{today} 호그와트 날씨 예보

{message}

#HogwartsWeather #호그와트날씨 #마법기상청
"""
        
        try:
            self.mastodon.status_post(full_message)
            print(f"날씨 예보 포스팅 완료: {weather}")
        except Exception as e:
            print(f"포스팅 실패: {str(e)}")

def main():
    # Mastodon 클라이언트 설정
    mastodon = Mastodon(
        access_token = 'your_access_token',
        api_base_url = 'https://your.mastodon.instance'
    )
    
    weather_bot = WeatherCasterBot(mastodon)
    
    # 매일 아침 8시에 날씨 포스팅
    schedule.every().day.at("08:00").do(weather_bot.post_daily_weather)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
