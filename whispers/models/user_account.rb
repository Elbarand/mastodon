class UserAccount
  attr_reader :id, :email, :characters

  def initialize(attributes = {})
    @id = attributes[:id]
    @email = attributes[:email]
    @characters = {}  # { character_name => Character }
    @active_character = nil
  end

  def add_character(character_name)
    return false if @characters.key?(character_name)
    
    @characters[character_name] = Character.new(
      name: character_name,
      owner_id: @id
    )
    true
  end

  def switch_character(character_name)
    if @characters.key?(character_name)
      @active_character = character_name
      true
    else
      false
    end
  end

  def post_rumor(content)
    return nil unless @active_character
    
    Rumor.create(
      character_name: @active_character,
      content: content,
      timestamp: Time.now
    )
  end

  def parse_message(message)
    return nil unless message.include?('/')
    
    character_name, content = message.split('/', 2)
    character_name = character_name.strip
    content = content.strip
    
    if @characters.key?(character_name)
      switch_character(character_name)
      post_rumor(content)
    else
      nil
    end
  end
end
