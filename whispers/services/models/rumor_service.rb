class RumorService
  def initialize
    @spreadsheet_manager = SpreadsheetManager.new
  end

  def create_rumor(character_name, content)
    rumor = Rumor.new(
      character_name: character_name,
      content: content
    )
    
    rumor.save
    broadcast_rumor(rumor)
    rumor
  end

  def get_recent_rumors(limit = 10)
    @spreadsheet_manager.get_recent_rumors(limit)
  end

  private

  def broadcast_rumor(rumor)
    # 여기서 온라인 플레이어들에게 소문을 전달하는 로직 구현
    Player.online.each do |player|
      rumor.deliver_to_player(player.id)
    end
  end
end
