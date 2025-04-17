class PlayerInfluenceTracker
  class << self
    def record(player_id, influence)
      player_influences[player_id] ||= []
      player_influences[player_id] << influence
      
      # 최근 10개의 영향만 유지
      player_influences[player_id] = player_influences[player_id].last(10)
      
      notify_player(player_id, influence)
    end

    def get_total_influence(player_id)
      influences = player_influences[player_id] || []
      return 0 if influences.empty?
      
      # 시간에 따른 영향력 감소 계산
      influences.sum do |inf|
        time_factor = calculate_time_decay(inf[:timestamp])
        inf[:influence_level] * time_factor
      end
    end

    private

    def player_influences
      @player_influences ||= {}
    end

    def calculate_time_decay(timestamp)
      hours_passed = ((Time.now - timestamp) / 3600).to_i
      # 24시간마다 영향력 50% 감소
      0.5 ** (hours_passed / 24.0)
    end

    def notify_player(player_id, influence)
      message = format_influence_message(influence)
      # 실제 알림 시스템과 연동
      puts "Player #{player_id} received rumor: #{message}"
    end

    def format_influence_message(influence)
      level_description = case influence[:influence_level]
      when 1..3 then "작은 소문이"
      when 4..6 then "흥미로운 소문이"
      when 7..8 then "중요한 소문이"
      else "충격적인 소문이"
      end

      "#{influence[:character_name]}의 #{level_description} 당신에게 도달했습니다."
    end
  end
end
