class Rumor
  attr_reader :id, :character_name, :content, :timestamp, :reactions

  def initialize(attributes = {})
    @id = attributes[:id]
    @character_name = attributes[:character_name]
    @content = attributes[:content]
    @timestamp = attributes[:timestamp] || Time.now
    @reactions = []
  end

  def self.create(attributes)
    rumor = new(attributes)
    # DB 저장 로직
    rumor
  end

  def format_display
    "[#{@character_name}] #{@content}"
  end
end
