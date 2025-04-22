
def run_psychological_check(player_sheet, caster_id, target_id, check_type, players_data, stat_choice=None):
    caster = next((p for p in players_data if p["ID"] == caster_id), None)
    target = next((p for p in players_data if p["ID"] == target_id), None)

    if not caster or not target:
        return "시전자 또는 대상이 존재하지 않습니다."

    if check_type == "지능판정":
        caster_stat = caster["지능"]
        desc = "지능 판정 (수사, 추리)"
    elif check_type == "협박판정":
        # STR 우선, 없으면 CHA
        caster_stat = caster.get("공격력") or caster.get("매력")
        desc = "협박/매력 판정 (증언 확보)"
    elif check_type == "거짓말탐지":
        if stat_choice not in ["지능", "매력", "공격력"]:
            return "선택 가능한 스탯은 지능, 매력, 공격력 중 하나입니다."
        caster_stat = caster[stat_choice]
        desc = f"거짓말 탐지 ({stat_choice} 기반)"
    else:
        return "알 수 없는 판정입니다."

    caster_roll = caster_stat + random.randint(1, 20)
    target_roll = target["의지"] + random.randint(1, 20)

    if caster_roll > target_roll:
        return f"✨ {desc} 성공! ({caster_roll} vs {target_roll})"
    else:
        return f"❌ {desc} 실패 ({caster_roll} vs {target_roll})"
