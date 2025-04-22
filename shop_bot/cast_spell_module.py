
import random

def cast_spell(player_sheet, spell_sheet, caster_id, target_id, spell_name, players_data):
    # 플레이어 정보 가져오기
    caster_row = next((row for row in players_data if row["ID"] == caster_id), None)
    target_row = next((row for row in players_data if row["ID"] == target_id), None)

    if not caster_row:
        return "시전자가 등록되어 있지 않습니다."
    if not target_row and target_id:
        return "대상이 존재하지 않습니다."

    # 마법 정보 불러오기
    spells = spell_sheet.get_all_records()
    spell = next((s for s in spells if s["마법명"] == spell_name), None)

    if not spell:
        return f"{spell_name} 마법은 존재하지 않습니다."

    mp_cost = int(spell["MP소모"])
    if caster_row["MP"] < mp_cost:
        return "마나가 부족합니다."

    # 판정 방식 해석 (간단한 예)
    if spell["판정방식"] == "MAG vs WIL":
        caster_score = caster_row["마력"] + random.randint(1, 20)
        target_score = target_row["의지"] + random.randint(1, 20)
    elif spell["판정방식"] == "INT + MAG vs 난이도":
        caster_score = caster_row["지능"] + caster_row["마력"] + random.randint(1, 20)
        target_score = int(spell.get("난이도", 15))  # 기본 난이도 15
    else:
        return "판정 방식을 해석할 수 없습니다."

    # MP 차감
    row_index = players_data.index(caster_row) + 2  # header 제외
    caster_row["MP"] -= mp_cost
    player_sheet.update_cell(row_index, 8, caster_row["MP"])

    # 판정 결과
    if caster_score > target_score:
        return f"✨ {spell['마법명']} 성공! ({spell['성공효과']})"
    else:
        return f"⚡ {spell['마법명']} 실패! 효과 없음."
