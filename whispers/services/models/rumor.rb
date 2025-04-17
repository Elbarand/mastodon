class Rumor
  attr_reader :id, :character_name, :content, :timestamp, :influence_level

  def initialize(attributes = {})
    @id = attributes[:id] || generate_id
    @character_name = attributes[:character_name]
    @content = attributes[:content]
    @timestamp = attributes[:timestamp] || Time.now
    @influence_level = attributes[:influence_level] || calculate_influence(@content)
    @delivered_to = Set.new
  end

  def save
    SpreadsheetManager.new.save_rumor(self)
    self
  end

  def deliver_to_player(player_id)
    return false if @delivered_to.include?(player_id)
    
    @delivered_to.add(player_id)
    apply_influence(player_id)
    true
  end

  private

  def generate_id
    "RMR#{Time.now.to_i}#{rand(1000)}"
  end

  def calculate_influence(content)
    return 0 unless content
    
    base_influence = 5
    keywords = ["비밀", "위험", "금지", "마법", "어둠"]
    keyword_count = keywords.count { |word| content.include?(word) }
    
    [base_influence + keyword_count, 10].min
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
