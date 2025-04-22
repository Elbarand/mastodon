class BossData:
    BOSSES = {
        '어둠의 상인': {
            'level': 3,
            'hp': 150,
            'attacks': ['저주', '어둠의 물건 투척', '악령 소환'],
            'drops': ['저주받은 목걸이', '어둠의 반지'],
            'required_item': None
        },
        '미로의 수호자': {
            'level': 4,
            'hp': 200,
            'attacks': ['미로 변형', '환각 주문', '시간 왜곡'],
            'drops': ['미로의 지도', '수호자의 홀'],
            'required_item': '저주받은 목걸이'
        },
        '지하철 악령': {
            'level': 3,
            'hp': 180,
            'attacks': ['영혼 흡수', '공포 주문', '혼돈 주문'],
            'drops': ['악령의 코어', '지하철 패스'],
            'required_item': None
        },
        '고위 죽음을 먹는 자': {
            'level': 4,
            'hp': 220,
            'attacks': ['아바다 케다브라', '크루시오', '임페리오'],
            'drops': ['죽음을 먹는 자의 마스크', '어둠의 마법서'],
            'required_item': '악령의 코어'
        },
        '어둠의 마왕': {
            'level': 5,
            'hp': 300,
            'attacks': ['살인 저주', '영혼 분열', '어둠의 폭풍'],
            'drops': ['마왕의 완드', '호크룩스'],
            'required_item': ['수호자의 홀', '어둠의 마법서']
        }
    }
