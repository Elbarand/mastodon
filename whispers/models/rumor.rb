class Rumor
  attr_reader :id, :character_name, :content, :timestamp, :influence_level

  def initialize(attributes = {})
    @id = attributes[:id]
    @character_name = attributes[:character_name]
    @content = attributes[:content]
    @timestamp = attributes[:timestamp] || Time.now
    @influence_level = calculate_influence(attributes[:content])
    @delivered_to = Set.new # 이미 전달된 플레이어 추적
  end

  def deliver_to_player(player_id)
    return false if @delivered_to.include?(player_id)
    
    @delivered_to.add(player_id)
    apply_influence(player_id)
    true
  end

  private

  def calculate_influence(content)
    # 소문의 영향력을 계산 (1-10 스케일)
    # 키워드나 문장 길이 등을 기반으로 계산
    base_influence = 5
    
    # 중요 키워드에 따른 영향력 조정
    keywords = ["비밀", "위험", "금지", "마법", "어둠"]
    keyword_count = keywords.count { |word| content.include?(word) }
    
    base_influence + keyword_count
  end

  def apply_influence(player_id)
    influence = {
      rumor_id: @id,
      character_name: @character_name,
      influence_level: @influence_level,
      timestamp: @timestamp
    }
    
    PlayerInfluenceTracker.record(player_id, influence)
  end
end
